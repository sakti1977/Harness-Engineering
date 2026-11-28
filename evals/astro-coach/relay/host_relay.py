# Host-side relay: the only path from the sandbox to the model API.
# Listens on a Unix socket, forwards /v1/* requests to api.anthropic.com, and injects the
# API key from a file that never enters the sandbox. Usage: host_relay.py <socket> <env-file>
import os, sys, socketserver, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler

SOCK, KEYFILE = sys.argv[1], sys.argv[2]
UPSTREAM = "https://api.anthropic.com"
HOP = {"host", "connection", "content-length", "x-api-key", "authorization",
       "accept-encoding", "transfer-encoding"}

def load_key():
    for line in open(KEYFILE):
        if line.startswith("ANTHROPIC_API_KEY="):
            return line.split("=", 1)[1].strip()
    raise SystemExit("no ANTHROPIC_API_KEY in key file")

KEY = load_key()

class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def forward(self):
        if not self.path.startswith("/v1/"):
            self.send_error(403, "only /v1/ paths are relayed")
            return
        n = int(self.headers.get("content-length") or 0)
        body = self.rfile.read(n) if n else None
        req = urllib.request.Request(UPSTREAM + self.path, data=body, method=self.command)
        for k, v in self.headers.items():
            if k.lower() not in HOP:
                req.add_header(k, v)
        req.add_header("x-api-key", KEY)
        try:
            resp = urllib.request.urlopen(req, timeout=900)
        except urllib.error.HTTPError as e:
            resp = e
        data = resp.read()
        code = resp.status if hasattr(resp, "status") else resp.code
        self.send_response(code)
        for k, v in resp.headers.items():
            if k.lower() not in ("content-length", "transfer-encoding", "connection", "content-encoding"):
                self.send_header(k, v)
        self.send_header("content-length", str(len(data)))
        self.send_header("connection", "close")
        self.end_headers()
        self.wfile.write(data)
        self.close_connection = True

    do_GET = forward
    do_POST = forward

    def log_message(self, *a):
        pass  # request bodies and keys are never logged

class Server(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True

if os.path.exists(SOCK):
    os.unlink(SOCK)
srv = Server(SOCK, Handler)
os.chmod(SOCK, 0o666)
srv.serve_forever()
