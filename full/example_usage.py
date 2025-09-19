"""
Example usage and test cases for the Python Dialplan Handler
"""

from dialplan_handler import (
    DialplanHandler, DialplanExtension, DialplanCondition, 
    DialplanAction, XMLBuilder
)
import json


def create_sample_dialplans():
    """Create some sample dialplan extensions for testing"""
    
    handler = DialplanHandler()
    
    print("Creating sample dialplan extensions...")
    
    # 1. Simple internal extension (1000-1099)
    handler.add_simple_extension(
        name="Local Extensions",
        context="default",
        destination_pattern="^(10[0-9][0-9])$",
        action_app="bridge",
        action_data="user/$1@$${domain}",
        order=100
    )
    
    # 2. Emergency services
    handler.add_simple_extension(
        name="Emergency 911",
        context="default", 
        destination_pattern="^(911|9911)$",
        action_app="bridge",
        action_data="sofia/gateway/emergency_trunk/$1",
        order=10
    )
    
    # 3. Outbound calls (9 + 10 digits)
    handler.add_simple_extension(
        name="Outbound Calls",
        context="default",
        destination_pattern="^9([0-9]{10})$",
        action_app="bridge", 
        action_data="sofia/gateway/trunk/$1",
        order=200
    )
    
    # 4. More complex extension with multiple conditions and actions
    complex_ext = DialplanExtension(
        name="Voicemail Access",
        uuid="vm-access-ext",
        context="default",
        order=150,
        enabled=True,
        conditions=[
            DialplanCondition(
                field="destination_number",
                expression="^\\*97$",
                regex=True
            ),
            DialplanCondition(
                field="caller_id_number", 
                expression="^(10[0-9][0-9])$",
                regex=True
            )
        ],
        actions=[
            DialplanAction(
                application="set",
                data="user_domain=$${domain}"
            ),
            DialplanAction(
                application="voicemail",
                data="check default $${domain} $2"
            )
        ]
    )
    
    handler.db.add_dialplan(complex_ext)
    
    # 5. Inbound call routing for public context
    inbound_ext = DialplanExtension(
        name="Inbound DID",
        uuid="inbound-did-ext", 
        context="public",
        order=100,
        enabled=True,
        conditions=[
            DialplanCondition(
                field="destination_number",
                expression="^(\\+?1?5551234567)$",
                regex=True
            )
        ],
        actions=[
            DialplanAction(
                application="set",
                data="domain_name=$${domain}"
            ),
            DialplanAction(
                application="transfer",
                data="1000 XML default"
            )
        ]
    )
    
    handler.db.add_dialplan(inbound_ext)
    
    print("Sample dialplans created successfully!")
    return handler


def test_xml_generation():
    """Test XML generation for different scenarios"""
    
    print("\n=== Testing XML Generation ===")
    
    handler = create_sample_dialplans()
    
    # Test 1: Generate XML for default context
    print("\n1. Testing default context XML generation:")
    xml = handler.handle_xml_request(
        section="dialplan",
        context="default", 
        destination_number="1001",
        domain_name="default.local"
    )
    print(xml)
    
    # Test 2: Generate XML for public context  
    print("\n2. Testing public context XML generation:")
    xml = handler.handle_xml_request(
        section="dialplan",
        context="public",
        destination_number="5551234567", 
        domain_name="default.local"
    )
    print(xml)
    
    # Test 3: Test caching
    print("\n3. Testing cache (should be faster second time):")
    import time
    
    start_time = time.time()
    xml1 = handler.handle_xml_request(section="dialplan", context="default")
    time1 = time.time() - start_time
    
    start_time = time.time() 
    xml2 = handler.handle_xml_request(section="dialplan", context="default")
    time2 = time.time() - start_time
    
    print(f"First call (database): {time1:.4f}s")
    print(f"Second call (cache): {time2:.4f}s")
    print(f"XML identical: {xml1 == xml2}")
    
    # Test 4: Test cache clearing
    print("\n4. Testing cache reload:")
    handler.reload_xml()
    xml3 = handler.handle_xml_request(section="dialplan", context="default")
    print(f"After reload, XML identical: {xml1 == xml3}")


def test_xml_builder():
    """Test the XML builder utility"""
    
    print("\n=== Testing XML Builder ===")
    
    xml = XMLBuilder()
    xml.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml.append('<document>')
    xml.append('  <section name="test">')
    test_data = XMLBuilder.sanitize('test & data < > " \'')
    xml.append(f'    <data value="{test_data}" />')
    xml.append('  </section>')
    xml.append('</document>')
    
    result = xml.build()
    print("XML Builder output:")
    print(result)
    
    # Test sanitization
    print("\nSanitization tests:")
    test_strings = [
        "normal text",
        "text with & ampersand", 
        "text with <tags>",
        'text with "quotes" and \'apostrophes\'',
        "text with ${variable} substitution",
        "mixed <test> & \"data\" with ${var}"
    ]
    
    for test_str in test_strings:
        sanitized = XMLBuilder.sanitize(test_str)
        print(f"Original: {test_str}")
        print(f"Sanitized: {sanitized}")
        print()


def create_realistic_pbx_dialplan():
    """Create a more realistic PBX dialplan setup"""
    
    print("\n=== Creating Realistic PBX Dialplan ===")
    
    handler = DialplanHandler()
    
    # Company extensions 2000-2999
    handler.add_simple_extension(
        name="Company Extensions",
        context="default",
        destination_pattern="^(2[0-9]{3})$",
        action_app="bridge",
        action_data="user/$1@$${domain}",
        order=100
    )
    
    # Conference rooms 3000-3099
    handler.add_simple_extension(
        name="Conference Rooms", 
        context="default",
        destination_pattern="^(30[0-9][0-9])$",
        action_app="conference",
        action_data="$1@default",
        order=110
    )
    
    # Operator (0)
    handler.add_simple_extension(
        name="Operator",
        context="default", 
        destination_pattern="^(0)$",
        action_app="bridge",
        action_data="user/2000@$${domain}",
        order=50
    )
    
    # International calls (011 + country + number)
    intl_ext = DialplanExtension(
        name="International Calls",
        uuid="intl-calls-ext",
        context="default",
        order=300,
        enabled=True,
        conditions=[
            DialplanCondition(
                field="destination_number",
                expression="^011([0-9]+)$",
                regex=True
            ),
            DialplanCondition(
                field="caller_id_number",
                expression="^(2[0-9]{3})$",
                regex=True,
                break_on_false="on-false"
            )
        ],
        actions=[
            DialplanAction(
                application="set",
                data="call_timeout=30"
            ),
            DialplanAction(
                application="set", 
                data="hangup_after_bridge=true"
            ),
            DialplanAction(
                application="bridge",
                data="sofia/gateway/international_trunk/011$1"
            )
        ],
        anti_actions=[
            DialplanAction(
                application="playback",
                data="not_authorized.wav"
            ),
            DialplanAction(
                application="hangup",
                data=""
            )
        ]
    )
    
    handler.db.add_dialplan(intl_ext)
    
    # Inbound call routing with time conditions
    inbound_business_hours = DialplanExtension(
        name="Inbound - Business Hours",
        uuid="inbound-biz-hours",
        context="public", 
        order=100,
        enabled=True,
        conditions=[
            DialplanCondition(
                field="destination_number",
                expression="^(\\+?1?555123456[0-9])$",
                regex=True
            ),
            DialplanCondition(
                field="${strftime(%w)}",
                expression="^([1-5])$",
                regex=True,
                break_on_false="on-false"
            ),
            DialplanCondition(
                field="${strftime(%H%M)}",
                expression="^((0[89]|1[0-6])[0-5][0-9])$",
                regex=True,
                break_on_false="on-false"
            )
        ],
        actions=[
            DialplanAction(
                application="set",
                data="domain_name=$${domain}"
            ),
            DialplanAction(
                application="ring_ready",
                data=""
            ),
            DialplanAction(
                application="bridge",
                data="user/2000@$${domain}"
            )
        ],
        anti_actions=[
            DialplanAction(
                application="voicemail",
                data="2000@$${domain}"
            )
        ]
    )
    
    handler.db.add_dialplan(inbound_business_hours)
    
    print("Realistic PBX dialplan created!")
    
    # Generate and show the XML
    print("\nGenerated default context XML:")
    xml = handler.handle_xml_request(
        section="dialplan",
        context="default",
        domain_name="company.com"
    )
    print(xml)
    
    return handler


if __name__ == "__main__":
    # Run all tests
    test_xml_builder()
    test_xml_generation() 
    create_realistic_pbx_dialplan()
    
    print("\n=== All tests completed! ===")
