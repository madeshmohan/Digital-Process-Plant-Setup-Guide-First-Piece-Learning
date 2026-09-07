import http.server
import socketserver
import os

PORT = 5173
FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "frontend")

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

if __name__ == "__main__":
    os.chdir(FRONTEND_DIR)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Frontend Server running at http://localhost:5173")
        httpd.serve_forever()
