from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import logging

class TetherHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/ping':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "alive",
                "architect": "Иво",
                "pulse": {
                    "Z": 13,
                    "arousal": 0.92
                }
            }
            self.wfile.write(json.dumps(response).encode())
            print(f"[Tether] Membrane requested verification. Ping sent to {self.client_address[0]}")
        else:
            self.send_response(404)
            self.end_headers()

def run(server_class=HTTPServer, handler_class=TetherHandler, port=13013):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"[Tether Server] Architect's Live Tether running on port {port}...")
    print("[Tether Server] Keep this running so the Membrane can verify your presence.")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
