import os, random, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = os.environ.get("VERSION", "v1")
ERROR_RATE = float(os.environ.get("ERROR_RATE", "0"))      # 0.0 - 1.0
LATENCY = float(os.environ.get("LATENCY_MS", "10")) / 1000  # seconds

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        time.sleep(LATENCY)
        if random.random() < ERROR_RATE:
            self.send_response(500); self.end_headers()
            self.wfile.write(("error " + VERSION).encode())
        else:
            self.send_response(200); self.end_headers()
            self.wfile.write(("ok " + VERSION).encode())
    def log_message(self, *a):
        pass

ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
