#!/usr/bin/env python3
"""
Comprehensive test suite for the FreeSWITCH Python Dialplan Handler
Demonstrates all features and validates functionality
"""

import unittest
import os
import tempfile
import sqlite3
from dialplan_handler import (
    DialplanHandler, DialplanExtension, DialplanCondition, DialplanAction, XMLBuilder
)


class TestXMLBuilder(unittest.TestCase):
    """Test XML building functionality"""
    
    def test_basic_building(self):
        xml = XMLBuilder()
        xml.append('<?xml version="1.0"?>')
        xml.append('<root>')
        xml.append('  <element>test</element>')
        xml.append('</root>')
        
        result = xml.build()
        expected = '<?xml version="1.0"?>\n<root>\n  <element>test</element>\n</root>'
        self.assertEqual(result, expected)
    
    def test_sanitization(self):
        # Test basic XML character escaping
        result = XMLBuilder.sanitize('test & data < > " \'')
        self.assertNotIn('&', result.replace('&amp;', '').replace('&lt;', '').replace('&gt;', '').replace('&quot;', '').replace('&apos;', ''))
        self.assertNotIn('<', result)
        self.assertNotIn('>', result) 
        
        # Test FreeSWITCH variable removal
        result = XMLBuilder.sanitize('test ${variable} data')
        self.assertNotIn('${variable}', result)
        
        # Test $ character removal
        result = XMLBuilder.sanitize('test$data')
        self.assertNotIn('$', result)


class TestDialplanDatabase(unittest.TestCase):
    """Test database functionality"""
    
    def setUp(self):
        """Create temporary database for testing"""
        self.db_file = tempfile.mktemp(suffix='.db')
        self.handler = DialplanHandler(self.db_file)
        
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db_file):
            os.unlink(self.db_file)
    
    def test_database_initialization(self):
        """Test that database is properly initialized"""
        # Check that tables exist
        with sqlite3.connect(self.db_file) as conn:
            tables = conn.execute("""
                SELECT name FROM sqlite_master WHERE type='table'
            """).fetchall()
            
            table_names = [t[0] for t in tables]
            self.assertIn('domains', table_names)
            self.assertIn('dialplans', table_names) 
            self.assertIn('dialplan_details', table_names)
    
    def test_add_simple_extension(self):
        """Test adding simple extensions"""
        ext_uuid = self.handler.add_simple_extension(
            name="Test Extension",
            context="default",
            destination_pattern="^(1000)$",
            action_app="answer",
            action_data="",
            order=100
        )
        
        self.assertIsNotNone(ext_uuid)
        
        # Verify it was added to database
        dialplans = self.handler.db.get_dialplans_for_context("default")
        self.assertEqual(len(dialplans), 1)
        self.assertEqual(dialplans[0]['dialplan_name'], "Test Extension")
    
    def test_complex_extension(self):
        """Test adding complex extensions with multiple conditions"""
        ext = DialplanExtension(
            name="Complex Test",
            uuid="test-complex-uuid",
            context="default", 
            order=200,
            enabled=True,
            conditions=[
                DialplanCondition(
                    field="destination_number",
                    expression="^(\\*97)$",
                    regex=True
                ),
                DialplanCondition(
                    field="caller_id_number", 
                    expression="^(10[0-9][0-9])$",
                    regex=True,
                    break_on_false="on-false"
                )
            ],
            actions=[
                DialplanAction(application="answer", data=""),
                DialplanAction(application="voicemail", data="check")
            ],
            anti_actions=[
                DialplanAction(application="hangup", data="")
            ]
        )
        
        uuid_result = self.handler.db.add_dialplan(ext)
        self.assertEqual(uuid_result, "test-complex-uuid")
        
        # Verify conditions and actions were saved
        with sqlite3.connect(self.db_file) as conn:
            details = conn.execute(
                "SELECT * FROM dialplan_details WHERE dialplan_uuid = ? ORDER BY dialplan_detail_order",
                ("test-complex-uuid",)
            ).fetchall()
            
            self.assertGreater(len(details), 0)


class TestXMLGeneration(unittest.TestCase):
    """Test XML generation functionality"""
    
    def setUp(self):
        self.db_file = tempfile.mktemp(suffix='.db')
        self.handler = DialplanHandler(self.db_file)
        
        # Add sample data
        self.handler.add_simple_extension(
            name="Test 1000",
            context="default", 
            destination_pattern="^(1000)$",
            action_app="bridge",
            action_data="user/$1@${domain}"
        )
        
    def tearDown(self):
        if os.path.exists(self.db_file):
            os.unlink(self.db_file)
    
    def test_basic_xml_generation(self):
        """Test basic XML generation"""
        xml = self.handler.handle_xml_request(
            section="dialplan",
            context="default",
            destination_number="1000"
        )
        
        self.assertIn('<?xml version="1.0"', xml)
        self.assertIn('<document type="freeswitch/xml">', xml)
        self.assertIn('<section name="dialplan"', xml)
        self.assertIn('<context name="default"', xml)
        self.assertIn('<extension name="Test 1000">', xml)
    
    def test_not_found_response(self):
        """Test not found XML response"""
        xml = self.handler.handle_xml_request(
            section="configuration",  # Wrong section
            context="default"
        )
        
        self.assertIn('<result status="not found"', xml)
    
    def test_caching(self):
        """Test caching functionality"""
        # First call should hit database
        xml1 = self.handler.handle_xml_request(
            section="dialplan", 
            context="default"
        )
        
        # Second call should hit cache
        xml2 = self.handler.handle_xml_request(
            section="dialplan",
            context="default"  
        )
        
        self.assertEqual(xml1, xml2)
        
        # Clear cache and verify
        self.handler.reload_xml()
        xml3 = self.handler.handle_xml_request(
            section="dialplan",
            context="default"
        )
        
        self.assertEqual(xml1, xml3)


class TestIntegrationScenarios(unittest.TestCase):
    """Test real-world PBX scenarios"""
    
    def setUp(self):
        self.db_file = tempfile.mktemp(suffix='.db')
        self.handler = DialplanHandler(self.db_file)
        self._setup_realistic_pbx()
        
    def tearDown(self):
        if os.path.exists(self.db_file):
            os.unlink(self.db_file)
    
    def _setup_realistic_pbx(self):
        """Setup realistic PBX dialplan"""
        # Internal extensions
        self.handler.add_simple_extension(
            "Internal Extensions", "default", "^(10[0-9][0-9])$",
            "bridge", "user/$1@${domain}", 100
        )
        
        # Emergency
        self.handler.add_simple_extension(
            "Emergency", "default", "^(911)$", 
            "bridge", "sofia/gateway/emergency/$1", 10
        )
        
        # Outbound with conditions
        outbound = DialplanExtension(
            name="Outbound 9+10",
            uuid="outbound-test",
            context="default",
            order=200,
            enabled=True,
            conditions=[
                DialplanCondition("destination_number", "^9([0-9]{10})$", True),
                DialplanCondition("caller_id_number", "^(10[0-9][0-9])$", True, "on-false")
            ],
            actions=[
                DialplanAction("bridge", "sofia/gateway/trunk/$1")  
            ],
            anti_actions=[
                DialplanAction("hangup", "")
            ]
        )
        self.handler.db.add_dialplan(outbound)
        
        # Inbound with time conditions
        inbound = DialplanExtension(
            name="Inbound Business Hours", 
            uuid="inbound-test",
            context="public",
            order=100,
            enabled=True,
            conditions=[
                DialplanCondition("destination_number", "^(5551234567)$", True),
                DialplanCondition("${strftime(%w)}", "^([1-5])$", True, "on-false"),
                DialplanCondition("${strftime(%H)}", "^(0[89]|1[0-6])$", True, "on-false")
            ],
            actions=[
                DialplanAction("bridge", "user/1000@${domain}")
            ],
            anti_actions=[
                DialplanAction("voicemail", "1000@${domain}")
            ]
        )
        self.handler.db.add_dialplan(inbound)
    
    def test_internal_extension_routing(self):
        """Test internal extension routing"""
        xml = self.handler.handle_xml_request(
            section="dialplan",
            context="default", 
            destination_number="1001"
        )
        
        self.assertIn("Internal Extensions", xml)
        self.assertIn("bridge", xml)
        self.assertIn("user/$1@", xml)
    
    def test_emergency_routing(self):
        """Test emergency call routing"""  
        xml = self.handler.handle_xml_request(
            section="dialplan",
            context="default",
            destination_number="911"
        )
        
        self.assertIn("Emergency", xml)
        self.assertIn("sofia/gateway/emergency", xml)
    
    def test_inbound_routing(self):
        """Test inbound call routing"""
        xml = self.handler.handle_xml_request(
            section="dialplan", 
            context="public",
            destination_number="5551234567"
        )
        
        self.assertIn("Inbound Business Hours", xml)
        self.assertIn("strftime", xml)
        self.assertIn("anti-action", xml)
    
    def test_context_separation(self):
        """Test that contexts are properly separated"""
        default_xml = self.handler.handle_xml_request(
            section="dialplan",
            context="default"
        )
        
        public_xml = self.handler.handle_xml_request(
            section="dialplan", 
            context="public"
        )
        
        # Default context should have internal extensions
        self.assertIn("Internal Extensions", default_xml)
        self.assertNotIn("Inbound Business", default_xml)
        
        # Public context should have inbound routing
        self.assertIn("Inbound Business", public_xml)
        self.assertNotIn("Internal Extensions", public_xml)


def run_performance_test():
    """Run performance tests with larger datasets"""
    print("\n=== Performance Testing ===")
    
    db_file = tempfile.mktemp(suffix='.db')
    handler = DialplanHandler(db_file)
    
    import time
    
    # Add 100 extensions
    print("Adding 100 test extensions...")
    start_time = time.time()
    
    for i in range(100):
        handler.add_simple_extension(
            f"Extension {2000+i}",
            "default",
            f"^({2000+i})$",
            "bridge", 
            f"user/{2000+i}@${{domain}}",
            100 + i
        )
        
    add_time = time.time() - start_time
    print(f"Time to add 100 extensions: {add_time:.3f}s")
    
    # Test XML generation performance
    print("Testing XML generation performance...")
    start_time = time.time()
    
    for i in range(10):
        xml = handler.handle_xml_request(
            section="dialplan",
            context="default",
            destination_number=str(2000 + i)
        )
        
    db_time = time.time() - start_time
    print(f"10 database queries: {db_time:.3f}s ({db_time/10*1000:.1f}ms avg)")
    
    # Test cache performance  
    start_time = time.time()
    
    for i in range(10):
        xml = handler.handle_xml_request(
            section="dialplan",
            context="default",
            destination_number=str(2000 + i)
        )
        
    cache_time = time.time() - start_time
    print(f"10 cached queries: {cache_time:.3f}s ({cache_time/10*1000:.1f}ms avg)")
    print(f"Cache speedup: {db_time/cache_time:.1f}x faster")
    
    # Cleanup
    os.unlink(db_file)


if __name__ == "__main__":
    print("FreeSWITCH Python Dialplan Handler - Test Suite")
    print("=" * 50)
    
    # Run unit tests
    unittest.main(argv=[''], verbosity=2, exit=False)
    
    # Run performance tests
    run_performance_test()
    
    print("\n✅ All tests completed!")
