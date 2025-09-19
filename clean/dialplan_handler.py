"""
Clean, production-ready FreeSWITCH Python Dialplan Handler
Simplified version with essential features only
"""

import psycopg2
import psycopg2.extras
import xml.etree.ElementTree as ET
import re
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import hashlib


@dataclass
class DialplanCondition:
    field: str
    expression: str
    break_on_false: str = "never"  # never, on-false, on-true
    

@dataclass 
class DialplanAction:
    application: str
    data: str
    inline: bool = False
    

@dataclass
class DialplanExtension:
    name: str
    uuid: str
    context: str
    order: int
    enabled: bool
    conditions: List[DialplanCondition]
    actions: List[DialplanAction]
    anti_actions: List[DialplanAction] = None
    

class XMLBuilder:
    def __init__(self):
        self.xml_parts = []
        
    def append(self, data: str):
        self.xml_parts.append(data)
        
    def build(self) -> str:
        return "\n".join(self.xml_parts)
    
    @staticmethod
    def sanitize(text: str) -> str:
        if text is None:
            return ""
        text = str(text)
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&apos;')
        return text


class DialplanCache:
    def __init__(self):
        self.cache = {}
        self.expire_times = {}
        
    def get(self, key: str) -> Optional[str]:
        if key in self.cache:
            import time
            if key in self.expire_times and time.time() < self.expire_times[key]:
                return self.cache[key]
            else:
                self.cache.pop(key, None)
                self.expire_times.pop(key, None)
        return None
        
    def set(self, key: str, value: str, expire_seconds: int = 3600):
        import time
        self.cache[key] = value
        self.expire_times[key] = time.time() + expire_seconds
        
    def clear(self):
        self.cache.clear()
        self.expire_times.clear()


class DialplanHandler:
    def __init__(self, host: str = "localhost", port: int = 5432, database: str = "dialplan", 
                 user: str = "postgres", password: str = "postgres"):
        self.db_config = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        self.cache = DialplanCache()
        self.init_database()
        
    def get_connection(self):
        return psycopg2.connect(**self.db_config)
        
    def init_database(self):
        print(f"Initializing database at {self.db_config['host']}:{self.db_config['port']}, DB: {self.db_config['database']}, User: {self.db_config['user']}")
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS public.domains (
                        domain_uuid VARCHAR(255) PRIMARY KEY,
                        domain_name VARCHAR(255) UNIQUE NOT NULL,
                        domain_enabled BOOLEAN DEFAULT TRUE
                    )
                """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS public.dialplans (
                        dialplan_uuid VARCHAR(255) PRIMARY KEY,
                        domain_uuid VARCHAR(255) NOT NULL,
                        dialplan_name VARCHAR(255) NOT NULL,
                        dialplan_context VARCHAR(255) NOT NULL,
                        dialplan_order INTEGER DEFAULT 999,
                        dialplan_enabled BOOLEAN DEFAULT TRUE,
                        dialplan_xml TEXT,
                        FOREIGN KEY (domain_uuid) REFERENCES domains (domain_uuid)
                    )
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_dialplans_context 
                    ON public.dialplans (dialplan_context, dialplan_order)
                """)
                
                cursor.execute("""
                    INSERT INTO public.domains (domain_uuid, domain_name) 
                    VALUES ('default-domain', 'default.local')
                    ON CONFLICT (domain_name) DO NOTHING
                """)
            conn.commit()
            print("Database initialized")
            
    def add_extension(self, extension: DialplanExtension, domain_name: str = "default.local") -> str:
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                # Get or create domain
                cursor.execute(
                    "SELECT domain_uuid FROM domains WHERE domain_name = %s", 
                    (domain_name,)
                )
                domain_result = cursor.fetchone()
                
                if not domain_result:
                    domain_uuid = f"domain-{hashlib.md5(domain_name.encode()).hexdigest()[:8]}"
                    cursor.execute(
                        "INSERT INTO domains (domain_uuid, domain_name) VALUES (%s, %s)",
                        (domain_uuid, domain_name)
                    )
                else:
                    domain_uuid = domain_result[0]
                    
                # Build and insert dialplan XML
                dialplan_xml = self._build_extension_xml(extension)
                cursor.execute("""
                    INSERT INTO dialplans 
                    (dialplan_uuid, domain_uuid, dialplan_name, dialplan_context, 
                     dialplan_order, dialplan_enabled, dialplan_xml)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (dialplan_uuid) DO UPDATE SET
                    domain_uuid = EXCLUDED.domain_uuid,
                    dialplan_name = EXCLUDED.dialplan_name,
                    dialplan_context = EXCLUDED.dialplan_context,
                    dialplan_order = EXCLUDED.dialplan_order,
                    dialplan_enabled = EXCLUDED.dialplan_enabled,
                    dialplan_xml = EXCLUDED.dialplan_xml
                """, (
                    extension.uuid, domain_uuid, extension.name, extension.context,
                    extension.order, extension.enabled, dialplan_xml
                ))
            conn.commit()
            
            return extension.uuid
            
    def _build_extension_xml(self, extension: DialplanExtension) -> str:
        xml = XMLBuilder()
        xml.append(f'<extension name="{XMLBuilder.sanitize(extension.name)}">')
        
        condition_count = len(extension.conditions)
        for condition in extension.conditions:
            break_attr = f' break="{condition.break_on_false}"' if condition.break_on_false != "never" else ''
            xml.append(f'    <condition field="{XMLBuilder.sanitize(condition.field)}" expression="{XMLBuilder.sanitize(condition.expression)}"{break_attr}>')
                
        for action in extension.actions:
            xml.append(f'        <action application="{XMLBuilder.sanitize(action.application)}" data="{XMLBuilder.sanitize(action.data)}"/>')
                
        if extension.anti_actions:
            for anti_action in extension.anti_actions:
                xml.append(f'        <anti-action application="{XMLBuilder.sanitize(anti_action.application)}" data="{XMLBuilder.sanitize(anti_action.data)}"/>')
                    
        for i in range(condition_count):
            xml.append('    </condition>')
            
        xml.append('</extension>')
        return xml.build()
        
    def get_dialplan_xml(self, context: str, destination_number: str = None, domain_name: str = None) -> str:
        cache_key = f"dialplan:{context}:{destination_number or 'any'}:{domain_name or 'any'}"
        
        # Try cache first
        cached = self.cache.get(cache_key)
        if cached:
            return cached
            
        # Generate from database
        xml = self._generate_xml(context, destination_number, domain_name)
        if xml:
            self.cache.set(cache_key, xml)
        return xml or self._not_found_xml()
        
    def _generate_xml(self, context: str, destination_number: str = None, domain_name: str = None) -> str:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                
                query = """
                    SELECT d.*, dom.domain_name 
                    FROM dialplans d
                    JOIN domains dom ON d.domain_uuid = dom.domain_uuid
                    WHERE d.dialplan_context = %s AND d.dialplan_enabled = TRUE
                """
                params = [context]
                
                if domain_name:
                    query += " AND dom.domain_name = %s"
                    params.append(domain_name)
                    
                query += " ORDER BY d.dialplan_order, d.dialplan_name"
                
                cursor.execute(query, params)
                dialplans = [dict(row) for row in cursor.fetchall()]
        
        if not dialplans:
            return None
            
        xml = XMLBuilder()
        xml.append('<?xml version="1.0" encoding="UTF-8" standalone="no"?>')
        xml.append('<document type="freeswitch/xml">')
        xml.append('    <section name="dialplan" description="">')
        
        context_attrs = f'name="{XMLBuilder.sanitize(context)}"'
        if destination_number:
            context_attrs += f' destination_number="{XMLBuilder.sanitize(destination_number)}"'
            
        xml.append(f'        <context {context_attrs}>')
        
        for dialplan in dialplans:
            if dialplan['dialplan_xml']:
                extension_lines = dialplan['dialplan_xml'].split('\n')
                for line in extension_lines:
                    if line.strip():
                        xml.append(f'            {line}')
                        
        xml.append('        </context>')
        xml.append('    </section>')
        xml.append('</document>')
        
        return xml.build()
        
    def _not_found_xml(self) -> str:
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
    <section name="result">
        <result status="not found" />
    </section>
</document>'''

    def add_simple_extension(self, name: str, context: str, pattern: str, 
                           app: str, data: str, order: int = 999, domain: str = "default.local") -> str:
        uuid = f"ext-{hashlib.md5(f'{name}-{context}-{pattern}'.encode()).hexdigest()[:8]}"
        
        extension = DialplanExtension(
            name=name, uuid=uuid, context=context, order=order, enabled=True,
            conditions=[DialplanCondition(field="destination_number", expression=pattern)],
            actions=[DialplanAction(application=app, data=data)]
        )
        
        return self.add_extension(extension, domain)
        
    def reload_cache(self):
        self.cache.clear()
        
    def list_dialplans(self, context: str = None) -> List[Dict]:
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                
                if context:
                    query = """
                        SELECT d.*, dom.domain_name 
                        FROM dialplans d JOIN domains dom ON d.domain_uuid = dom.domain_uuid
                        WHERE d.dialplan_context = %s ORDER BY d.dialplan_order
                    """
                    params = [context]
                else:
                    query = """
                        SELECT d.*, dom.domain_name 
                        FROM dialplans d JOIN domains dom ON d.domain_uuid = dom.domain_uuid
                        ORDER BY d.dialplan_context, d.dialplan_order
                    """
                    params = []
                    
                cursor.execute(query, params)
                return [dict(row) for row in cursor.fetchall()]
