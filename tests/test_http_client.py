import shutil
import ssl
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import requests

from src.http_client import get_icon_session


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


class QuietHTTPServer(HTTPServer):
    def handle_error(self, request, client_address):
        pass  # Rejected TLS handshakes are expected


@unittest.skipUnless(shutil.which("openssl"), "requires the openssl command")
class SystemTrustSessionTests(unittest.TestCase):
    """Runs a local HTTPS server with a self-signed certificate that no trust store contains."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.cert = Path(cls.tmp.name) / "cert.pem"
        key = Path(cls.tmp.name) / "key.pem"
        subprocess.run(
            [
                "openssl",
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-nodes",
                "-days",
                "1",
                "-keyout",
                str(key),
                "-out",
                str(cls.cert),
                "-subj",
                "/CN=localhost",
                "-addext",
                "subjectAltName=IP:127.0.0.1",
            ],
            check=True,
            capture_output=True,
        )
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cls.cert, key)
        cls.server = QuietHTTPServer(("127.0.0.1", 0), Handler)
        cls.server.socket = context.wrap_socket(cls.server.socket, server_side=True)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"https://127.0.0.1:{cls.server.server_port}/"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.tmp.cleanup()

    def test_untrusted_certificate_is_rejected(self):
        with self.assertRaises(requests.exceptions.SSLError):
            get_icon_session().get(self.url, timeout=5)

    def test_explicit_ca_bundle_is_respected(self):
        response = get_icon_session().get(self.url, timeout=5, verify=str(self.cert))
        self.assertEqual(response.text, "ok")


if __name__ == "__main__":
    unittest.main()
