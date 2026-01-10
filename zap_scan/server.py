"""HTTP server for serving scan reports."""

import http.server
import os
import socketserver
from pathlib import Path


class ReportServer:
    """Simple HTTP server for serving scan reports."""

    def __init__(self, reports_dir: str = "reports", port: int = 8000):
        """Initialize the server."""
        self.reports_dir = Path(reports_dir)
        self.port = port

    def serve(self):
        """Start the HTTP server."""
        # Change to reports directory
        if not self.reports_dir.exists():
            raise FileNotFoundError(
                f"Reports directory not found: {self.reports_dir}\n"
                "Run a scan first using: zap-scan scan <url>"
            )

        os.chdir(self.reports_dir)

        # Create server
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.TCPServer(("", self.port), handler) as httpd:
            print(f"🌐 Serving reports at http://localhost:{self.port}/")
            print(f"📂 Reports directory: {self.reports_dir.absolute()}")
            print(f"🔗 Open http://localhost:{self.port}/index.html in your browser")
            print()
            print("Press Ctrl+C to stop the server")
            print()

            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print()
                print("Server stopped.")
