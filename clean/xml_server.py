#!/usr/bin/env python3
"""
Simple HTTP server for FreeSWITCH mod_xml_curl integration
Clean, minimal implementation
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs
import logging
from dialplan_handler import DialplanHandler


class FreeSWITCHHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, dialplan_handler=None, **kwargs):
        self.dialplan_handler = dialplan_handler
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle FreeSWITCH mod_xml_curl requests"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = parse_qs(post_data)
            
            # Extract parameters
            section = params.get('section', [''])[0]
            context = params.get('Caller-Context', [''])[0] or params.get('Hunt-Context', [''])[0]
            destination = params.get('Caller-Destination-Number', [''])[0]
            domain = params.get('variable_domain_name', [''])[0] or params.get('domain', [''])[0]
            
            print(f"Request: section={section}, context={context}, destination={destination}")
            
            if section == 'dialplan':
                xml = self.dialplan_handler.get_dialplan_xml(context, destination, domain)
            else:
                xml = self._not_found()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml')
            self.end_headers()
            self.wfile.write(xml.encode('utf-8'))
            
        except Exception as e:
            print(f"Error: {e}")
            self.send_error(500)
    
    def do_GET(self):
        """Handle test requests"""
        if self.path.startswith('/dialplan'):
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            query = parse_qs(parsed.query)
            
            context = query.get('context', ['default'])[0]
            destination = query.get('destination', [None])[0]
            domain = query.get('domain', [None])[0]
            
            xml = self.dialplan_handler.get_dialplan_xml(context, destination, domain)
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml')
            self.end_headers()
            self.wfile.write(xml.encode('utf-8'))
            
        elif self.path == '/reload':
            self.dialplan_handler.reload_cache()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Cache cleared')
            
        else:
            help_html = """
            <html><body>
            <h1>FreeSWITCH Python Dialplan Handler</h1>
            <p>Test endpoints:</p>
            <ul>
                <li><a href="/dialplan?context=default">/dialplan?context=default</a></li>
                <li><a href="/dialplan?context=default&destination=1001">/dialplan?context=default&destination=1001</a></li>
                <li><a href="/reload">/reload</a> - Clear cache</li>
            </ul>
            </body></html>
            """
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(help_html.encode('utf-8'))
    
    def _not_found(self):
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
    <section name="result">
        <result status="not found" />
    </section>
</document>'''
    
    def log_message(self, format, *args):
        print(format % args)


def main():
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='FreeSWITCH PostgreSQL Dialplan Server')
    parser.add_argument('--host', default='localhost', help='Server host (default: localhost)')
    parser.add_argument('--port', type=int, default=8080, help='Server port (default: 8080)')
    parser.add_argument('--db-host', default='localhost', help='PostgreSQL host (default: localhost)')
    parser.add_argument('--db-port', type=int, default=5432, help='PostgreSQL port (default: 5432)')
    parser.add_argument('--db-name', default='dialplan', help='PostgreSQL database name (default: dialplan)')
    parser.add_argument('--db-user', default='postgres', help='PostgreSQL user (default: postgres)')
    parser.add_argument('--db-password', default='123qwe', help='PostgreSQL password (default: 123qwe)')
    
    # Support old command line format for backward compatibility
    if len(sys.argv) >= 4 and not any(arg.startswith('--') for arg in sys.argv[1:]):
        host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
        port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
        # Third argument was db_path in SQLite version, now we'll use it as db_name
        db_name = sys.argv[3] if len(sys.argv) > 3 else "dialplan"
        if db_name.endswith('.db'):
            db_name = db_name[:-3]  # Remove .db extension
        
        args = argparse.Namespace(
            host=host, port=port, db_host='localhost', db_port=5432,
            db_name=db_name, db_user='postgres', db_password='postgres'
        )
    else:
        args = parser.parse_args()
    
    handler = DialplanHandler(
        host=args.db_host,
        port=args.db_port,
        database=args.db_name,
        user=args.db_user,
        password=args.db_password
    )
    
    def handler_factory(*args_inner, **kwargs):
        return FreeSWITCHHandler(*args_inner, dialplan_handler=handler, **kwargs)
    
    server = HTTPServer((args.host, args.port), handler_factory)
    
    print(f"FreeSWITCH Dialplan Server starting on {args.host}:{args.port}")
    print(f"PostgreSQL Database: {args.db_user}@{args.db_host}:{args.db_port}/{args.db_name}")
    print(f"Configure FreeSWITCH: <param name=\"gateway-url\" value=\"http://{args.host}:{args.port}/\" />")
    print("Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped")


if __name__ == "__main__":
    main()
