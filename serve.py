"""Local dev server for site/ that tells the browser not to cache anything.

Usage: python3 serve.py [port]   (default port 8000)
"""
import functools
import http.server
import pathlib
import socket
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
SITE = pathlib.Path(__file__).resolve().parent / "site"


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Pages, styles and the locales/*.json text change often while editing.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


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
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
