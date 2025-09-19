#!/usr/bin/env python3
"""
Simple usage example for the clean dialplan handler with PostgreSQL
"""

from dialplan_handler import DialplanHandler, DialplanExtension, DialplanCondition, DialplanAction
import os

def main():
    print("Clean FreeSWITCH Python Dialplan Handler (PostgreSQL)")
    print("=" * 50)
    
    # Initialize handler with PostgreSQL connection
    # Adjust these parameters for your PostgreSQL setup
    handler = DialplanHandler(
        host="localhost",
        port=5432,
        database="dialplan",
        user="postgres",
        password="123qwe"
    )
    print("✓ Handler initialized with PostgreSQL")
    
    # Add some basic extensions
    handler.add_simple_extension(
        "Internal Extensions", "default", "^(10[0-9][0-9])$", 
        "bridge", "user/$1@${domain}", 100
    )
    print("✓ Added internal extensions")
    
    handler.add_simple_extension(
        "Emergency", "default", "^(911)$",
        "bridge", "sofia/gateway/emergency/$1", 10  
    )
    print("✓ Added emergency routing")
    
    # Add complex extension with multiple conditions
    complex_ext = DialplanExtension(
        name="Outbound with Auth",
        uuid="outbound-auth",
        context="default",
        order=200,
        enabled=True,
        conditions=[
            DialplanCondition("destination_number", "^9([0-9]{10})$"),
            DialplanCondition("caller_id_number", "^(10[0-9][0-9])$", "on-false")
        ],
        actions=[
            DialplanAction("bridge", "sofia/gateway/trunk/$1")
        ],
        anti_actions=[
            DialplanAction("playback", "not_authorized.wav"),
            DialplanAction("hangup", "")
        ]
    )
    
    handler.add_extension(complex_ext)
    print("✓ Added outbound with authorization")
    
    # Test XML generation
    print("\nGenerating XML for default context...")
    xml = handler.get_dialplan_xml("default", "1001")
    print(xml)
    
    print("\nDialplans in database:")
    dialplans = handler.list_dialplans()
    for dp in dialplans:
        print(f"  {dp['dialplan_name']} (context: {dp['dialplan_context']}, order: {dp['dialplan_order']})")
    
    print(f"\n✓ Clean dialplan handler working! Database: {os.path.abspath('clean_dialplan.db')}")

if __name__ == "__main__":
    main()
