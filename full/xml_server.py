"""
HTTP server interface for FreeSWITCH mod_xml_curl integration
Provides REST API endpoints that FreeSWITCH can call to get dialplan XML
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import logging
from dialplan_handler import DialplanHandler


class XMLCurlHandler(BaseHTTPRequestHandler):
    """HTTP handler for FreeSWITCH mod_xml_curl requests"""
    
    def __init__(self, *args, dialplan_handler=None, **kwargs):
        self.dialplan_handler = dialplan_handler or DialplanHandler()
        self.logger = logging.getLogger('xml_curl_handler')
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests from FreeSWITCH mod_xml_curl"""
        try:
            # Parse content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            # Read POST data
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parse form data (FreeSWITCH sends form-encoded data)
            parsed_data = parse_qs(post_data)
            
            # Extract FreeSWITCH parameters
            params = {}
            for key, values in parsed_data.items():
                params[key] = values[0] if values else ''
            
            # Log the request
            self.logger.info(f"XML request: section={params.get('section')}, "
                           f"context={params.get('Caller-Context')}, "
                           f"destination={params.get('Caller-Destination-Number')}")
            
            # Handle dialplan requests
            if params.get('section') == 'dialplan':
                xml_response = self.dialplan_handler.handle_xml_request(
                    section='dialplan',
                    context=params.get('Caller-Context') or params.get('Hunt-Context'),
                    destination_number=params.get('Caller-Destination-Number'),
                    domain_name=params.get('variable_domain_name') or params.get('domain'),
                    hostname=params.get('hostname'),
                    **params
                )
            else:
                # Return not found for non-dialplan requests
                xml_response = self._not_found_response()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml')
            self.send_header('Content-Length', str(len(xml_response.encode('utf-8'))))
            self.end_headers()
            self.wfile.write(xml_response.encode('utf-8'))
            
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            self.send_error(500, str(e))
    
    def do_GET(self):
        """Handle GET requests (for testing/debugging)"""
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if parsed_url.path == '/dialplan':
            # Test dialplan generation
            context = query_params.get('context', ['default'])[0]
            destination = query_params.get('destination', [None])[0]
            domain = query_params.get('domain', [None])[0]
            
            xml_response = self.dialplan_handler.handle_xml_request(
                section='dialplan',
                context=context,
                destination_number=destination,
                domain_name=domain
            )
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml')
            self.end_headers()
            self.wfile.write(xml_response.encode('utf-8'))
            
        elif parsed_url.path == '/reload':
            # Reload dialplans (clear cache)
            self.dialplan_handler.reload_xml()
            
            response = {"status": "success", "message": "Dialplan cache cleared"}
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif parsed_url.path == '/status':
            # Server status
            response = {
                "status": "running",
                "dialplan_handler": "active",
                "cache_entries": len(self.dialplan_handler.cache.cache)
            }
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        else:
            # Default response with usage info
            html_response = """
            <html>
            <head><title>FreeSWITCH XML Handler</title></head>
            <body>
            <h1>FreeSWITCH Python XML Handler</h1>
            <p>This server provides dialplan XML for FreeSWITCH via mod_xml_curl.</p>
            
            <h2>Test Endpoints:</h2>
            <ul>
                <li><a href="/dialplan?context=default">/dialplan?context=default</a> - Test default context</li>
                <li><a href="/dialplan?context=public&destination=5551234567">/dialplan?context=public&destination=5551234567</a> - Test public context with destination</li>
                <li><a href="/reload">/reload</a> - Clear dialplan cache</li>
                <li><a href="/status">/status</a> - Server status</li>
            </ul>
            
            <h2>FreeSWITCH Configuration:</h2>
            <p>Configure mod_xml_curl in FreeSWITCH to POST to this server:</p>
            <pre>
&lt;configuration name="xml_curl.conf" description="cURL XML Gateway"&gt;
  &lt;bindings&gt;
    &lt;binding name="dialplan"&gt;
      &lt;param name="gateway-url" value="http://localhost:8080/" /&gt;
      &lt;param name="gateway-credentials" value="user:pass" /&gt;
      &lt;param name="disable-100-continue" value="true" /&gt;
    &lt;/binding&gt;
  &lt;/bindings&gt;
&lt;/configuration&gt;
            </pre>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html_response.encode('utf-8'))
    
    def _not_found_response(self):
        """Return XML not found response"""
        return '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<document type="freeswitch/xml">
    <section name="result">
        <result status="not found" />
    </section>
</document>'''
    
    def log_message(self, format, *args):
        """Override to use Python logging instead of stderr"""
        self.logger.info(format % args)


def create_xml_server(host='localhost', port=8080, db_path="dialplan.db"):
    """Create and configure the XML server"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] [%(levelname)s] %(name)s: %(message)s'
    )
    
    # Create dialplan handler
    handler = DialplanHandler(db_path)
    
    # Create server with handler injection
    def handler_factory(*args, **kwargs):
        return XMLCurlHandler(*args, dialplan_handler=handler, **kwargs)
    
    server = HTTPServer((host, port), handler_factory)
    
    print(f"Starting FreeSWITCH XML Handler server on {host}:{port}")
    print(f"Database: {db_path}")
    print("\nConfigure FreeSWITCH mod_xml_curl to POST to:")
    print(f"  http://{host}:{port}/")
    print("\nTest endpoints:")
    print(f"  http://{host}:{port}/dialplan?context=default")
    print(f"  http://{host}:{port}/reload")
    print(f"  http://{host}:{port}/status")
    print("\nPress Ctrl+C to stop")
    
    return server, handler


if __name__ == "__main__":
    import sys
    
    # Parse command line arguments
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
    db_path = sys.argv[3] if len(sys.argv) > 3 else "dialplan.db"
    
    try:
        server, handler = create_xml_server(host, port, db_path)
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        server.shutdown()
        print("Server stopped")
