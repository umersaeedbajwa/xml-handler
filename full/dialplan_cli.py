"""
Command-line interface for managing dialplans
Provides easy CLI commands to add, list, test, and manage dialplans
"""

import argparse
import json
import sys
import uuid
import sqlite3
from datetime import datetime
from dialplan_handler import (
    DialplanHandler, DialplanExtension, DialplanCondition, DialplanAction
)


class DialplanCLI:
    """Command-line interface for dialplan management"""
    
    def __init__(self, db_path="dialplan.db"):
        self.handler = DialplanHandler(db_path)
        
    def list_dialplans(self, context=None, domain=None):
        """List all dialplans or filter by context/domain"""
        dialplans = []
        
        if context:
            dialplans = self.handler.db.get_dialplans_for_context(context, domain)
        else:
            # Get all dialplans
            with sqlite3.connect(self.handler.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                query = """
                    SELECT d.*, dom.domain_name 
                    FROM dialplans d
                    JOIN domains dom ON d.domain_uuid = dom.domain_uuid
                    ORDER BY d.dialplan_context, d.dialplan_order, d.dialplan_name
                """
                dialplans = [dict(row) for row in conn.execute(query).fetchall()]
        
        if not dialplans:
            print("No dialplans found")
            return
            
        print(f"{'Name':<30} {'Context':<15} {'Order':<6} {'Domain':<20} {'Enabled':<8}")
        print("-" * 85)
        
        for dp in dialplans:
            enabled = "Yes" if dp['dialplan_enabled'] else "No"
            print(f"{dp['dialplan_name']:<30} {dp['dialplan_context']:<15} "
                  f"{dp['dialplan_order']:<6} {dp['domain_name']:<20} {enabled:<8}")
    
    def add_simple(self, name, context, pattern, app, data, order=999, domain="default.local"):
        """Add a simple dialplan extension"""
        try:
            ext_uuid = self.handler.add_simple_extension(
                name=name,
                context=context, 
                destination_pattern=pattern,
                action_app=app,
                action_data=data,
                order=order,
                domain_name=domain
            )
            print(f"Added dialplan extension: {name} (UUID: {ext_uuid})")
            return ext_uuid
        except Exception as e:
            print(f"Error adding dialplan: {e}")
            return None
    
    def test_xml(self, context, destination=None, domain=None):
        """Test XML generation for given parameters"""
        print(f"Testing XML generation:")
        print(f"  Context: {context}")
        print(f"  Destination: {destination}")
        print(f"  Domain: {domain}")
        print()
        
        xml = self.handler.handle_xml_request(
            section="dialplan",
            context=context,
            destination_number=destination,
            domain_name=domain
        )
        
        print("Generated XML:")
        print(xml)
    
    def reload_cache(self):
        """Clear the dialplan cache"""
        self.handler.reload_xml()
        print("Dialplan cache cleared")
    
    def show_stats(self):
        """Show dialplan statistics"""
        with sqlite3.connect(self.handler.db.db_path) as conn:
            # Count dialplans by context
            context_counts = conn.execute("""
                SELECT dialplan_context, COUNT(*) as count
                FROM dialplans 
                WHERE dialplan_enabled = 1
                GROUP BY dialplan_context
                ORDER BY dialplan_context
            """).fetchall()
            
            # Count domains
            domain_count = conn.execute("SELECT COUNT(*) FROM domains").fetchone()[0]
            
            # Total dialplans
            total_dialplans = conn.execute("""
                SELECT COUNT(*) FROM dialplans WHERE dialplan_enabled = 1
            """).fetchone()[0]
            
        print("Dialplan Statistics:")
        print(f"  Total domains: {domain_count}")
        print(f"  Total enabled dialplans: {total_dialplans}")
        print(f"  Cache entries: {len(self.handler.cache.cache)}")
        print()
        
        print("Dialplans by context:")
        for context, count in context_counts:
            print(f"  {context}: {count}")
    
    def export_json(self, output_file):
        """Export all dialplans to JSON"""
        with sqlite3.connect(self.handler.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Export domains
            domains = [dict(row) for row in conn.execute("SELECT * FROM domains").fetchall()]
            
            # Export dialplans with details
            dialplans = []
            for row in conn.execute("SELECT * FROM dialplans ORDER BY dialplan_context, dialplan_order").fetchall():
                dialplan = dict(row)
                
                # Get details
                details = [dict(detail) for detail in conn.execute(
                    "SELECT * FROM dialplan_details WHERE dialplan_uuid = ? ORDER BY dialplan_detail_order",
                    (dialplan['dialplan_uuid'],)
                ).fetchall()]
                
                dialplan['details'] = details
                dialplans.append(dialplan)
        
        export_data = {
            "domains": domains,
            "dialplans": dialplans,
            "exported_at": str(datetime.now())
        }
        
        with open(output_file, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        print(f"Exported {len(dialplans)} dialplans to {output_file}")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="FreeSWITCH Dialplan Management CLI")
    parser.add_argument('--db', default='dialplan.db', help='Database file path')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List dialplans')
    list_parser.add_argument('--context', help='Filter by context')
    list_parser.add_argument('--domain', help='Filter by domain')
    
    # Add command
    add_parser = subparsers.add_parser('add', help='Add simple dialplan')
    add_parser.add_argument('name', help='Dialplan name')
    add_parser.add_argument('context', help='Dialplan context')
    add_parser.add_argument('pattern', help='Destination number pattern (regex)')
    add_parser.add_argument('app', help='Application to execute')
    add_parser.add_argument('data', help='Application data')
    add_parser.add_argument('--order', type=int, default=999, help='Execution order')
    add_parser.add_argument('--domain', default='default.local', help='Domain name')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test XML generation')
    test_parser.add_argument('context', help='Context to test')
    test_parser.add_argument('--destination', help='Destination number')
    test_parser.add_argument('--domain', help='Domain name')
    
    # Other commands
    subparsers.add_parser('reload', help='Clear dialplan cache')
    subparsers.add_parser('stats', help='Show dialplan statistics')
    
    export_parser = subparsers.add_parser('export', help='Export dialplans to JSON')
    export_parser.add_argument('file', help='Output file path')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    cli = DialplanCLI(args.db)
    
    try:
        if args.command == 'list':
            cli.list_dialplans(args.context, args.domain)
            
        elif args.command == 'add':
            cli.add_simple(args.name, args.context, args.pattern, args.app, args.data, 
                          args.order, args.domain)
            
        elif args.command == 'test':
            cli.test_xml(args.context, args.destination, args.domain)
            
        elif args.command == 'reload':
            cli.reload_cache()
            
        elif args.command == 'stats':
            cli.show_stats()
            
        elif args.command == 'export':
            cli.export_json(args.file)
            
    except Exception as e:
        print(f"Error: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())
