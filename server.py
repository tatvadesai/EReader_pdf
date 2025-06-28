#!/usr/bin/env python3
import http.server
import socketserver
import os
import urllib.parse

class PDFReaderHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            # Read the HTML file
            with open('index.html', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Inject the API key
            api_key = os.environ.get('GEMINI_API_KEY', '')
            content = content.replace('__GEMINI_API_KEY__', api_key)
            
            self.wfile.write(content.encode('utf-8'))
        else:
            # Serve other files normally
            super().do_GET()

if __name__ == "__main__":
    PORT = 5000
    with socketserver.TCPServer(("0.0.0.0", PORT), PDFReaderHandler) as httpd:
        print(f"PDF E-Reader server running on port {PORT}")
        print(f"Visit http://localhost:{PORT}")
        httpd.serve_forever()