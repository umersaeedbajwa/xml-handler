"""
Python XML Handler for FreeSWITCH Dialplan Management
Replicates FusionPBX's Lua-based XML handler functionality
"""

import sqlite3
import xml.etree.ElementTree as ET
from xml.dom import minidom
import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class DialplanCondition:
    """Represents a dialplan condition"""
    field: str
    expression: str
    regex: bool = True
    break_on_false: str = "never"  # never, on-false, on-true
    

@dataclass
class DialplanAction:
    """Represents a dialplan action"""
    application: str
    data: str
    inline: bool = False
    

@dataclass
class DialplanExtension:
    """Represents a complete dialplan extension"""
    name: str
    uuid: str
    context: str
    order: int
    enabled: bool
    conditions: List[DialplanCondition]
    actions: List[DialplanAction]
    anti_actions: List[DialplanAction] = None
    continue_on_match: bool = False
    

class XMLBuilder:
    """XML building utility similar to FusionPBX's xml.lua"""
    
    def __init__(self):
        self.xml_parts = []
        
    def append(self, data: str):
        """Add XML content to the builder"""
        self.xml_parts.append(data)
        
    def build(self) -> str:
        """Concatenate and return the complete XML"""
        return "\n".join(self.xml_parts)
    
    @staticmethod
    def sanitize(text: str) -> str:
        """Sanitize text for XML output, similar to xml.sanitize in Lua"""
        if text is None:
            return ""
        
        text = str(text)
        
        # Escape XML characters first
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        
        # Don't remove FreeSWITCH variables or $ - they're needed for dialplan logic
        # Only remove dangerous script execution patterns
        text = re.sub(r'\$\{lua [^}]+\}', '', text)
        
        return text


class DialplanCache:
    """Simple in-memory cache for dialplan XML"""
    
    def __init__(self):
        self.cache = {}
        self.expire_times = {}
        
    def get(self, key: str) -> Optional[str]:
        """Get cached XML if not expired"""
        if key in self.cache:
            # Simple time-based expiration (3600 seconds default)
            import time
            if key in self.expire_times and time.time() < self.expire_times[key]:
                return self.cache[key]
            else:
                # Expired, remove from cache
                self.cache.pop(key, None)
                self.expire_times.pop(key, None)
        return None
        
    def set(self, key: str, value: str, expire_seconds: int = 3600):
        """Set cached XML with expiration"""
        import time
        self.cache[key] = value
        self.expire_times[key] = time.time() + expire_seconds
        
    def clear(self, pattern: str = None):
        """Clear cache entries matching pattern"""
        if pattern:
            keys_to_remove = [k for k in self.cache.keys() if pattern in k]
            for key in keys_to_remove:
                self.cache.pop(key, None)
                self.expire_times.pop(key, None)
        else:
            self.cache.clear()
            self.expire_times.clear()


class DialplanDatabase:
    """Database interface for dialplan management"""
    
    def __init__(self, db_path: str = "dialplan.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS domains (
                    domain_uuid TEXT PRIMARY KEY,
                    domain_name TEXT UNIQUE NOT NULL,
                    domain_enabled BOOLEAN DEFAULT 1
                );
                
                CREATE TABLE IF NOT EXISTS dialplans (
                    dialplan_uuid TEXT PRIMARY KEY,
                    domain_uuid TEXT NOT NULL,
                    dialplan_name TEXT NOT NULL,
                    dialplan_context TEXT NOT NULL,
                    dialplan_order INTEGER DEFAULT 999,
                    dialplan_enabled BOOLEAN DEFAULT 1,
                    dialplan_xml TEXT,
                    hostname TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (domain_uuid) REFERENCES domains (domain_uuid)
                );
                
                CREATE TABLE IF NOT EXISTS dialplan_details (
                    dialplan_detail_uuid TEXT PRIMARY KEY,
                    dialplan_uuid TEXT NOT NULL,
                    dialplan_detail_type TEXT NOT NULL, -- condition, action, anti-action
                    dialplan_detail_tag TEXT NOT NULL,  -- condition, action, anti-action
                    dialplan_detail_field TEXT,         -- destination_number, caller_id_number, etc
                    dialplan_detail_value TEXT,         -- regex or action data
                    dialplan_detail_order INTEGER DEFAULT 999,
                    dialplan_detail_break TEXT DEFAULT 'never',
                    dialplan_detail_inline BOOLEAN DEFAULT 0,
                    FOREIGN KEY (dialplan_uuid) REFERENCES dialplans (dialplan_uuid)
                );
                
                CREATE INDEX IF NOT EXISTS idx_dialplans_context ON dialplans (dialplan_context, dialplan_order);
                CREATE INDEX IF NOT EXISTS idx_dialplan_details_order ON dialplan_details (dialplan_uuid, dialplan_detail_order);
                
                -- Insert default domain if not exists
                INSERT OR IGNORE INTO domains (domain_uuid, domain_name) 
                VALUES ('default-domain-uuid', 'default.local');
            """)
            
    def add_dialplan(self, extension: DialplanExtension, domain_name: str = "default.local") -> str:
        """Add a new dialplan extension"""
        with sqlite3.connect(self.db_path) as conn:
            # Get domain_uuid
            domain_uuid = conn.execute(
                "SELECT domain_uuid FROM domains WHERE domain_name = ?", 
                (domain_name,)
            ).fetchone()
            
            if not domain_uuid:
                # Create domain if it doesn't exist
                domain_uuid = f"domain-{hashlib.md5(domain_name.encode()).hexdigest()}"
                conn.execute(
                    "INSERT INTO domains (domain_uuid, domain_name) VALUES (?, ?)",
                    (domain_uuid, domain_name)
                )
            else:
                domain_uuid = domain_uuid[0]
                
            # Insert dialplan
            conn.execute("""
                INSERT INTO dialplans 
                (dialplan_uuid, domain_uuid, dialplan_name, dialplan_context, 
                 dialplan_order, dialplan_enabled, dialplan_xml)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                extension.uuid, domain_uuid, extension.name, extension.context,
                extension.order, extension.enabled, self._build_extension_xml(extension)
            ))
            
            # Insert conditions and actions
            detail_order = 0
            for condition in extension.conditions:
                detail_order += 10
                conn.execute("""
                    INSERT INTO dialplan_details 
                    (dialplan_detail_uuid, dialplan_uuid, dialplan_detail_type, 
                     dialplan_detail_tag, dialplan_detail_field, dialplan_detail_value,
                     dialplan_detail_order, dialplan_detail_break)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"{extension.uuid}-cond-{detail_order}", extension.uuid, 
                    "condition", "condition", condition.field, condition.expression,
                    detail_order, condition.break_on_false
                ))
                
            for action in extension.actions:
                detail_order += 10
                conn.execute("""
                    INSERT INTO dialplan_details 
                    (dialplan_detail_uuid, dialplan_uuid, dialplan_detail_type,
                     dialplan_detail_tag, dialplan_detail_field, dialplan_detail_value,
                     dialplan_detail_order, dialplan_detail_inline)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"{extension.uuid}-act-{detail_order}", extension.uuid,
                    "action", "action", action.application, action.data,
                    detail_order, action.inline
                ))
                
            if extension.anti_actions:
                for anti_action in extension.anti_actions:
                    detail_order += 10
                    conn.execute("""
                        INSERT INTO dialplan_details 
                        (dialplan_detail_uuid, dialplan_uuid, dialplan_detail_type,
                         dialplan_detail_tag, dialplan_detail_field, dialplan_detail_value,
                         dialplan_detail_order, dialplan_detail_inline)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        f"{extension.uuid}-anti-{detail_order}", extension.uuid,
                        "anti-action", "anti-action", anti_action.application, anti_action.data,
                        detail_order, anti_action.inline
                    ))
                    
            conn.commit()
            return extension.uuid
            
    def get_dialplans_for_context(self, context: str, domain_name: str = None, 
                                 destination_number: str = None) -> List[Dict]:
        """Get dialplans for a specific context"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if domain_name:
                query = """
                    SELECT d.*, dom.domain_name, dom.domain_enabled 
                    FROM dialplans d
                    JOIN domains dom ON d.domain_uuid = dom.domain_uuid
                    WHERE d.dialplan_context = ? AND dom.domain_name = ? 
                    AND d.dialplan_enabled = 1 AND dom.domain_enabled = 1
                    ORDER BY d.dialplan_order, d.dialplan_name
                """
                params = (context, domain_name)
            else:
                query = """
                    SELECT d.*, dom.domain_name, dom.domain_enabled 
                    FROM dialplans d
                    JOIN domains dom ON d.domain_uuid = dom.domain_uuid
                    WHERE d.dialplan_context = ? 
                    AND d.dialplan_enabled = 1 AND dom.domain_enabled = 1
                    ORDER BY d.dialplan_order, d.dialplan_name
                """
                params = (context,)
                
            return [dict(row) for row in conn.execute(query, params).fetchall()]
            
    def _build_extension_xml(self, extension: DialplanExtension) -> str:
        """Build XML for a single extension"""
        xml = XMLBuilder()
        
        continue_attr = ' continue="true"' if extension.continue_on_match else ''
        xml.append(f'<extension name="{XMLBuilder.sanitize(extension.name)}"{continue_attr}>')
        
        # Track condition nesting
        condition_count = 0
        
        for condition in extension.conditions:
            condition_count += 1
            break_attr = f' break="{condition.break_on_false}"' if condition.break_on_false != "never" else ''
            xml.append(f'    <condition field="{XMLBuilder.sanitize(condition.field)}" expression="{XMLBuilder.sanitize(condition.expression)}"{break_attr}>')
                
        # Add actions inside the innermost condition
        for action in extension.actions:
            if action.inline:
                xml.append(f'        <action application="{XMLBuilder.sanitize(action.application)}" data="{XMLBuilder.sanitize(action.data)}" inline="true"/>')
            else:
                xml.append(f'        <action application="{XMLBuilder.sanitize(action.application)}" data="{XMLBuilder.sanitize(action.data)}"/>')
                
        if extension.anti_actions:
            for anti_action in extension.anti_actions:
                if anti_action.inline:
                    xml.append(f'        <anti-action application="{XMLBuilder.sanitize(anti_action.application)}" data="{XMLBuilder.sanitize(anti_action.data)}" inline="true"/>')
                else:
                    xml.append(f'        <anti-action application="{XMLBuilder.sanitize(anti_action.application)}" data="{XMLBuilder.sanitize(anti_action.data)}"/>')
                    
        # Close all conditions in reverse order
        for i in range(condition_count):
            xml.append('    </condition>')
            
        xml.append('</extension>')
        return xml.build()


class DialplanHandler:
    """Main dialplan XML handler class"""
    
    def __init__(self, db_path: str = "dialplan.db"):
        self.db = DialplanDatabase(db_path)
        self.cache = DialplanCache()
        self.logger = self._setup_logging()
        
    def _setup_logging(self):
        """Setup logging similar to FreeSWITCH console logs"""
        logger = logging.getLogger('dialplan_handler')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] [dialplan_handler] %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
        
    def handle_xml_request(self, section: str, context: str = None, 
                          destination_number: str = None, domain_name: str = None,
                          hostname: str = None, **kwargs) -> str:
        """Handle XML request from FreeSWITCH (main entry point)"""
        
        if section != "dialplan":
            return self._not_found_xml()
            
        # Build cache key
        cache_key = self._build_cache_key(context, destination_number, domain_name, hostname)
        
        # Try cache first
        cached_xml = self.cache.get(cache_key)
        if cached_xml:
            self.logger.info(f"{cache_key} source: cache")
            return cached_xml
            
        # Generate XML from database
        xml_string = self._generate_dialplan_xml(context, destination_number, domain_name, hostname)
        
        # Cache the result
        if xml_string:
            self.cache.set(cache_key, xml_string)
            self.logger.info(f"{cache_key} source: database")
            
        return xml_string or self._not_found_xml()
        
    def _build_cache_key(self, context: str, destination_number: str = None, 
                        domain_name: str = None, hostname: str = None) -> str:
        """Build cache key for dialplan lookup"""
        key_parts = ["dialplan", context or "default"]
        
        if destination_number:
            key_parts.append(destination_number)
        if domain_name:
            key_parts.append(domain_name)
        if hostname:
            key_parts.append(hostname)
            
        return ":".join(key_parts)
        
    def _generate_dialplan_xml(self, context: str, destination_number: str = None,
                              domain_name: str = None, hostname: str = None) -> str:
        """Generate complete dialplan XML from database"""
        
        xml = XMLBuilder()
        
        # XML document header
        xml.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
        xml.append('<document type="freeswitch/xml">')
        xml.append('    <section name="dialplan" description="">')
        
        # Context header with attributes
        context_attrs = f'name="{XMLBuilder.sanitize(context or "default")}"'
        if destination_number:
            context_attrs += f' destination_number="{XMLBuilder.sanitize(destination_number)}"'
        if hostname:
            context_attrs += f' hostname="{XMLBuilder.sanitize(hostname)}"'
            
        xml.append(f'        <context {context_attrs}>')
        
        # Get dialplans from database
        dialplans = self.db.get_dialplans_for_context(context or "default", domain_name, destination_number)
        
        # Add each dialplan's XML
        for dialplan in dialplans:
            if dialplan['dialplan_xml']:
                # Indent the extension XML properly
                extension_lines = dialplan['dialplan_xml'].split('\n')
                for line in extension_lines:
                    if line.strip():
                        xml.append(f'            {line}')
                        
        # Close context and document
        xml.append('        </context>')
        xml.append('    </section>')
        xml.append('</document>')
        
        return xml.build()
        
    def _not_found_xml(self) -> str:
        """Return 'not found' XML response"""
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
    <section name="result">
        <result status="not found" />
    </section>
</document>'''

    def reload_xml(self):
        """Clear cache to force reload (similar to FreeSWITCH reloadxml)"""
        self.cache.clear()
        self.logger.info("XML cache cleared - dialplans will be reloaded from database")
        
    def add_simple_extension(self, name: str, context: str, destination_pattern: str, 
                           action_app: str, action_data: str, order: int = 999,
                           domain_name: str = "default.local") -> str:
        """Helper method to add simple extensions easily"""
        
        extension_uuid = f"ext-{hashlib.md5(f'{name}-{context}-{destination_pattern}'.encode()).hexdigest()}"
        
        extension = DialplanExtension(
            name=name,
            uuid=extension_uuid,
            context=context,
            order=order,
            enabled=True,
            conditions=[
                DialplanCondition(
                    field="destination_number",
                    expression=destination_pattern,
                    regex=True
                )
            ],
            actions=[
                DialplanAction(
                    application=action_app,
                    data=action_data
                )
            ]
        )
        
        return self.db.add_dialplan(extension, domain_name)
