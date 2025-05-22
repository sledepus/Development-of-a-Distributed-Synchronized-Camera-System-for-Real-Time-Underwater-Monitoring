import http.server
import socketserver

PORT = 8000

class WebpageHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path in ["/", "/dashboard.html"]:
            self.path = "/dashboard.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_error(404, "File not found")

with socketserver.TCPServer(("", PORT), WebpageHandler) as httpd:
    print(f"Serving dashboard at http://localhost:{PORT}/")
    httpd.serve_forever()
