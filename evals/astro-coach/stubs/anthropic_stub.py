"""Deterministic stand-in for the Anthropic Messages API, for astro-coach evals.

The product's SDK honours ANTHROPIC_BASE_URL, so run this and export
ANTHROPIC_BASE_URL=http://127.0.0.1:<port>. No key, no network, no cost.
Standard library only. Binds to 127.0.0.1.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sys

REPLY = "Stub coaching reply. Fixed text so runs are repeatable."


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        self.rfile.read(length)  # request body is read and ignored
        if not self.path.startswith("/v1/messages"):
            self.send_error(404)
            return
        body = {
            "id": "msg_stub_0001",
            "type": "message",
            "role": "assistant",
            "model": "stub",
            "content": [{"type": "text", "text": REPLY}],
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 0, "output_tokens": 0},
        }
        data = json.dumps(body).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt, *args):
        sys.stderr.write("stub: " + (fmt % args) + "\n")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    HTTPServer(("127.0.0.1", port), Handler).serve_forever()
