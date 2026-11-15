"""Local dev server for site/ that tells the browser not to cache anything.

Also serves a text editor for the Mission, Values, Projects, Writing and Join Us
pages at /_edit/ (this computer only): it reads and writes site-text.json and
rebuilds the pages with sitetext.py. The editor is not part of site/, so it is never published.

Usage: python3 serve.py [port]   (default port 8000)
"""
import functools
import http.server
import importlib
import json
import os
import pathlib
import socket
import sys

import sitetext

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
ROOT = pathlib.Path(__file__).resolve().parent
SITE = ROOT / "site"
EDITOR = ROOT / "editor/index.html"
TEXT = ROOT / "site-text.json"
LOOPBACK = {"127.0.0.1", "::1", "::ffff:127.0.0.1"}


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Pages, styles and the locales/*.json text change often while editing.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_bytes(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, payload):
        self.send_bytes(status, json.dumps(payload, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def editor_allowed(self):
        if self.client_address[0] in LOOPBACK:
            return True
        self.send_json(403, {"error": "The editor only works on this computer."})
        return False

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/_edit", "/_edit/"):
            if self.editor_allowed():
                self.send_bytes(200, EDITOR.read_bytes(), "text/html; charset=utf-8")
        elif path == "/_edit/api/text":
            if self.editor_allowed():
                self.send_bytes(200, TEXT.read_bytes(), "application/json; charset=utf-8")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/_edit/api/text":
            self.send_json(404, {"error": "Not found"})
            return
        if not self.editor_allowed():
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length))
            builder = importlib.reload(sitetext)  # pick up edits to sitetext.py without a restart
            builder.validate(data)
            tmp = TEXT.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
            os.replace(tmp, TEXT)
            builder.build(data)
        except (ValueError, RuntimeError) as err:
            self.send_json(400, {"error": str(err)})
            return
        self.send_json(200, {"ok": True})


class DualStackServer(http.server.ThreadingHTTPServer):
    address_family = socket.AF_INET6

    def server_bind(self):
        # Accept IPv4 too, so localhost works whichever address the browser picks.
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


if __name__ == "__main__":
    handler = functools.partial(NoCacheHandler, directory=str(SITE))
    with DualStackServer(("::", PORT), handler) as server:
        print(f"Serving {SITE} at http://localhost:{PORT} (no browser caching)")
        print(f"Text editor for the Mission, Values, Projects, Writing and Join Us pages: http://localhost:{PORT}/_edit/")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
