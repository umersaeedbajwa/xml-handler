#!/usr/bin/env python3
"""
Setup script to create a working dialplan environment with sample data
"""

from dialplan_handler import DialplanHandler, DialplanExtension, DialplanCondition, DialplanAction
import sys
import os


def create_sample_environment():
    """Create a complete sample dialplan environment"""
    
    print("Setting up FreeSWITCH Python Dialplan Handler...")
    print("=" * 50)
    
    # Initialize handler
    handler = DialplanHandler("sample_dialplan.db")
    
    print("✓ Database initialized")
    
    # 1. Basic internal extensions
    handler.add_simple_extension(
        name="Internal Extensions 1000-1099",
        context="default", 
        destination_pattern="^(10[0-9][0-9])$",
        action_app="bridge",
        action_data="user/$1@${domain}",
        order=100,
        domain_name="company.local"
    )
    print("✓ Added internal extensions 1000-1099")
    
    # 2. Conference rooms
    handler.add_simple_extension(
        name="Conference Rooms 3000-3099",
        context="default",
        destination_pattern="^(30[0-9][0-9])$", 
        action_app="conference",
        action_data="$1@default",
        order=110,
        domain_name="company.local"
    )
    print("✓ Added conference rooms 3000-3099")
    
    # 3. Emergency services
    handler.add_simple_extension(
        name="Emergency 911",
        context="default",
        destination_pattern="^(911|9911)$",
        action_app="bridge", 
        action_data="sofia/gateway/emergency_trunk/$1",
        order=10,
        domain_name="company.local"
    )
    print("✓ Added emergency 911 routing")
    
    # 4. Operator (0)
    handler.add_simple_extension(
        name="Operator",
        context="default",
        destination_pattern="^(0)$",
        action_app="bridge",
        action_data="user/1000@${domain}",
        order=50,
        domain_name="company.local"
    )
    print("✓ Added operator extension")
    
    # 5. Voicemail access
    vm_ext = DialplanExtension(
        name="Voicemail Access",
        uuid="vm-access-12345",
        context="default",
        order=150, 
        enabled=True,
        conditions=[
            DialplanCondition(
                field="destination_number",
                expression="^\\*97$",
                regex=True
            )
        ],
        actions=[
            DialplanAction(
                application="answer",
                data=""
            ),
            DialplanAction(
                application="sleep",
                data="1000"
            ),
            DialplanAction(
                application="voicemail",
                data="check default ${domain} ${caller_id_number}"
            )
        ]
    )
    handler.db.add_dialplan(vm_ext, "company.local")
    print("✓ Added voicemail access (*97)")
    
    # 6. Outbound calls with authorization
    outbound_ext = DialplanExtension(
        name="Outbound Calls - 9+10digits",
        uuid="outbound-9-12345",
        context="default",
        order=200,
        enabled=True,
        conditions=[
            DialplanCondition(
                field="destination_number", 
                expression="^9([0-9]{10})$",
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
            DialplanAction(
                application="set",
                data="effective_caller_id_number=${caller_id_number}"
            ),
            DialplanAction(
                application="set", 
                data="hangup_after_bridge=true"
            ),
            DialplanAction(
                application="bridge",
                data="sofia/gateway/trunk/$1"
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
    handler.db.add_dialplan(outbound_ext, "company.local")
    print("✓ Added outbound calling (9+10 digits)")
    
    # 7. Inbound DID routing with time conditions
    inbound_ext = DialplanExtension(
        name="Inbound Main Number - Business Hours",
        uuid="inbound-main-12345",
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
                expression="^([1-5])$",  # Monday-Friday
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
            DialplanAction(
                application="set",
                data="domain_name=${domain}"
            ),
            DialplanAction(
                application="ring_ready",
                data=""
            ),
            DialplanAction(
                application="bridge",
                data="user/1000@${domain}"
            )
        ],
        anti_actions=[
            DialplanAction(
                application="voicemail", 
                data="1000@${domain}"
            )
        ]
    )
    handler.db.add_dialplan(inbound_ext, "company.local")
    print("✓ Added inbound DID with business hours")
    
    # 8. After hours / weekend routing
    after_hours_ext = DialplanExtension(
        name="Inbound Main Number - After Hours", 
        uuid="inbound-after-12345",
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
            DialplanAction(
                application="answer",
                data=""
            ),
            DialplanAction(
                application="playback",
                data="after_hours_greeting.wav"
            ),
            DialplanAction(
                application="voicemail",
                data="1000@${domain}"
            )
        ]
    )
    handler.db.add_dialplan(after_hours_ext, "company.local")
    print("✓ Added after-hours inbound handling")
    
    print("\nSample dialplan environment created successfully!")
    print("\nDatabase: sample_dialplan.db")
    print("Domain: company.local")
    
    print("\nTest the setup:")
    print("1. Start the HTTP server:")
    print("   python xml_server.py localhost 8080 sample_dialplan.db")
    print("\n2. Test XML generation:")
    print("   python dialplan_cli.py --db=sample_dialplan.db test default --destination=1001")
    print("\n3. List all dialplans:")  
    print("   python dialplan_cli.py --db=sample_dialplan.db list")
    
    # Generate sample XML to show it works
    print("\n" + "="*50)
    print("SAMPLE XML OUTPUT (default context, extension 1001):")
    print("="*50)
    
    xml = handler.handle_xml_request(
        section="dialplan",
        context="default",
        destination_number="1001",
        domain_name="company.local"
    )
    print(xml)
    
    return handler


if __name__ == "__main__":
    try:
        handler = create_sample_environment()
        
        print(f"\n✅ Setup complete! Database ready at: {os.path.abspath('sample_dialplan.db')}")
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
