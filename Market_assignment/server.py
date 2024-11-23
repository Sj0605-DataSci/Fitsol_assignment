from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse as urlparse

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        query_components = urlparse.parse_qs(urlparse.urlparse(self.path).query)
        authorization_code = query_components.get('code', [None])[0]
        state = query_components.get('state', [None])[0]

        if authorization_code:
            print(f"Authorization Code: {authorization_code}")
        else:
            print("Authorization Code: None")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Authorization code captured. You can close this window.')

server = HTTPServer(('localhost', 8000), CallbackHandler)
print("Server running at http://localhost:8000/callback. Waiting for the authorization code...")
server.serve_forever()