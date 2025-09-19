#!/usr/bin/env python3
"""
FreeSWITCH Python Dialplan Handler - Live Demo
Shows complete working example with realistic PBX scenarios
"""

from dialplan_handler import DialplanHandler, DialplanExtension, DialplanCondition, DialplanAction
import os
import time


def main():
    print("🚀 FreeSWITCH Python Dialplan Handler - Live Demo")
    print("=" * 55)
    
    # Initialize handler
    db_file = "demo_pbx.db"
    if os.path.exists(db_file):
        os.unlink(db_file)
    
    handler = DialplanHandler(db_file)
    print("✅ Initialized dialplan handler with SQLite database")
    
    # Create a realistic company PBX setup
    print("\n📞 Setting up Company PBX (ACME Corp)...")
    
    # 1. Internal extensions (2000-2999)
    handler.add_simple_extension(
        name="ACME Employee Extensions",
        context="default",
        destination_pattern="^(2[0-9]{3})$",
        action_app="bridge", 
        action_data="user/$1@acme.corp",
        order=100,
        domain_name="acme.corp"
    )
    print("  ✅ Added employee extensions 2000-2999")
    
    # 2. Conference rooms (3000-3099)  
    handler.add_simple_extension(
        name="Conference Rooms",
        context="default",
        destination_pattern="^(30[0-9][0-9])$",
        action_app="conference",
        action_data="$1@acme_conferences",
        order=110,
        domain_name="acme.corp"
    )
    print("  ✅ Added conference rooms 3000-3099")
    
    # 3. Operator and directory
    handler.add_simple_extension(
        name="Operator", 
        context="default",
        destination_pattern="^(0|operator)$",
        action_app="bridge",
        action_data="user/2000@acme.corp",
        order=50,
        domain_name="acme.corp"
    )
    print("  ✅ Added operator (0)")
    
    # 4. Emergency services (highest priority)
    handler.add_simple_extension(
        name="Emergency Services",
        context="default", 
        destination_pattern="^(911|9911)$",
        action_app="bridge",
        action_data="sofia/gateway/emergency_trunk/$1",
        order=10,
        domain_name="acme.corp"
    )
    print("  ✅ Added emergency routing (911)")
    
    # 5. Voicemail access with caller ID validation
    vm_ext = DialplanExtension(
        name="Voicemail Access",
        uuid="acme-vm-access",
        context="default",
        order=150,
        enabled=True,
        conditions=[
            DialplanCondition(
                field="destination_number",
                expression="^\\*98$",
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
            DialplanAction(application="answer", data=""),
            DialplanAction(application="sleep", data="1000"),
            DialplanAction(application="voicemail", data="check default acme.corp $2")
        ],
        anti_actions=[
            DialplanAction(application="playback", data="access_denied.wav"),
            DialplanAction(application="hangup", data="")
        ]
    )
    handler.db.add_dialplan(vm_ext, "acme.corp")
    print("  ✅ Added voicemail access (*98) with security")
    
    # 6. Outbound calling with authorization
    outbound_ext = DialplanExtension(
        name="Outbound Calls - 9+1+10digits",
        uuid="acme-outbound-us",
        context="default", 
        order=200,
        enabled=True,
        conditions=[
            DialplanCondition(
                field="destination_number",
                expression="^9(1[0-9]{10})$",
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
            DialplanAction(application="set", data="effective_caller_id_number=+15551234567"),
            DialplanAction(application="set", data="hangup_after_bridge=true"),
            DialplanAction(application="bridge", data="sofia/gateway/us_trunk/$1")
        ],
        anti_actions=[
            DialplanAction(application="playback", data="not_authorized.wav"),
            DialplanAction(application="hangup", data="")
        ]
    )
    handler.db.add_dialplan(outbound_ext, "acme.corp")
    print("  ✅ Added outbound calling (9+1+10 digits) with auth")
    
    # 7. Inbound DID with business hours routing
    inbound_biz = DialplanExtension(
        name="Main Number - Business Hours",
        uuid="acme-inbound-biz",
        context="public",
        order=100, 
        enabled=True,
        conditions=[
            DialplanCondition(
                field="destination_number",
                expression="^(\\+?1?5551234567)$",
                regex=True
            ),
            DialplanCondition(
                field="${strftime(%w)}", 
                expression="^([1-5])$",  # Mon-Fri
                regex=True,
                break_on_false="on-false"
            ),
            DialplanCondition(
                field="${strftime(%H)}",
                expression="^(0[89]|1[0-6])$",  # 8 AM - 4 PM
                regex=True,
                break_on_false="on-false" 
            )
        ],
        actions=[
            DialplanAction(application="set", data="domain_name=acme.corp"),
            DialplanAction(application="answer", data=""),
            DialplanAction(application="playback", data="welcome_to_acme.wav"),
            DialplanAction(application="bridge", data="user/2000@acme.corp")
        ],
        anti_actions=[
            DialplanAction(application="answer", data=""),
            DialplanAction(application="playback", data="after_hours_message.wav"),
            DialplanAction(application="voicemail", data="2000@acme.corp")
        ]
    )
    handler.db.add_dialplan(inbound_biz, "acme.corp")
    print("  ✅ Added inbound main number with business hours")
    
    # 8. After hours catch-all
    inbound_after = DialplanExtension(
        name="Main Number - After Hours",
        uuid="acme-inbound-after",
        context="public",
        order=200,
        enabled=True,
        conditions=[
            DialplanCondition(
                field="destination_number", 
                expression="^(\\+?1?5551234567)$",
                regex=True
            )
        ],
        actions=[
            DialplanAction(application="answer", data=""),
            DialplanAction(application="playback", data="after_hours_full_message.wav"),
            DialplanAction(application="voicemail", data="2000@acme.corp")
        ]
    )
    handler.db.add_dialplan(inbound_after, "acme.corp")
    print("  ✅ Added after-hours fallback")
    
    print("\n📊 PBX Setup Complete! Statistics:")
    
    # Show stats
    import sqlite3
    with sqlite3.connect(db_file) as conn:
        total_exts = conn.execute("SELECT COUNT(*) FROM dialplans WHERE dialplan_enabled = 1").fetchone()[0]
        contexts = conn.execute("SELECT DISTINCT dialplan_context FROM dialplans").fetchall()
        
    print(f"  📈 Total active dialplans: {total_exts}")
    print(f"  🏢 Contexts: {', '.join([c[0] for c in contexts])}")
    
    print("\n🧪 Testing XML Generation...")
    
    # Test scenarios
    test_cases = [
        ("Employee calls 2001", "default", "2001", "acme.corp"),
        ("Employee dials 911", "default", "911", "acme.corp"), 
        ("Employee calls operator", "default", "0", "acme.corp"),
        ("Employee joins meeting", "default", "3001", "acme.corp"),
        ("Employee checks voicemail", "default", "*98", "acme.corp"),
        ("Employee makes outbound call", "default", "915551234567", "acme.corp"),
        ("Inbound call to main number", "public", "5551234567", "acme.corp"),
    ]
    
    for description, context, dest, domain in test_cases:
        start_time = time.time()
        xml = handler.handle_xml_request(
            section="dialplan",
            context=context,
            destination_number=dest,
            domain_name=domain
        )
        gen_time = time.time() - start_time
        
        extensions_found = xml.count('<extension name=')
        print(f"  ✅ {description}: {extensions_found} extensions, {gen_time*1000:.1f}ms")
        
        # Test caching on second call
        start_time = time.time()  
        xml2 = handler.handle_xml_request(
            section="dialplan",
            context=context,
            destination_number=dest,
            domain_name=domain
        )
        cache_time = time.time() - start_time
        
        if xml == xml2:
            speedup = gen_time / cache_time if cache_time > 0 else float('inf')
            print(f"     🚀 Cached: {cache_time*1000:.1f}ms ({speedup:.1f}x faster)")
    
    print(f"\n💾 Database saved as: {os.path.abspath(db_file)}")
    
    print("\n🌐 Ready for FreeSWITCH Integration!")
    print("Configure mod_xml_curl in FreeSWITCH to use this handler:")
    print(f"  1. Start HTTP server: python xml_server.py localhost 8080 {db_file}")
    print("  2. Configure xml_curl.conf:")
    print("     <param name=\"gateway-url\" value=\"http://localhost:8080/\" />")
    
    print("\n🎯 Sample XML Output (employee calls 2001):")
    print("-" * 50)
    xml = handler.handle_xml_request(
        section="dialplan",
        context="default", 
        destination_number="2001",
        domain_name="acme.corp"
    )
    
    # Pretty print just the extensions part
    lines = xml.split('\n')
    for line in lines:
        if '<extension' in line or '<condition' in line or '<action' in line or '</extension>' in line:
            print(line)
            if '</extension>' in line:
                break
    
    print("\n✨ Demo complete! Your Python dialplan handler is ready.")
    print(f"📁 Project files created in: {os.path.abspath('.')}")
    
    return handler


if __name__ == "__main__":
    handler = main()
