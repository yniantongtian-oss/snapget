"""Exercise the actual loopback server without external media requests."""
import http.client
import json
import threading
import unittest
from http.server import ThreadingHTTPServer

from web.server import SnapGetRequestHandler


class TestLocalHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), SnapGetRequestHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, path, body=None, headers=None):
        conn = http.client.HTTPConnection(*self.server.server_address, timeout=5)
        try:
            conn.request("GET" if body is None else "POST", path, body, headers or {})
            response = conn.getresponse()
            return response.status, response.read()
        finally:
            conn.close()

    def test_page_loads(self):
        status, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn(b"SnapGet", body)

    def test_empty_parse_rejected(self):
        status, body = self.request("/api/parse", b"{}")
        self.assertEqual(status, 400)
        self.assertIs(json.loads(body)["success"], False)

    def test_empty_search_rejected(self):
        self.assertEqual(self.request("/api/search", b"{}")[0], 400)

    def test_malformed_json_and_utf8_rejected(self):
        for body in (b"{", b"\xff", b"[]", b"null"):
            with self.subTest(body=body):
                self.assertEqual(self.request("/api/parse", body)[0], 400)

    def test_wrong_field_types_rejected(self):
        self.assertEqual(self.request("/api/parse", b'{"text":123}')[0], 400)
        self.assertEqual(self.request("/api/search", b'{"keyword":null}')[0], 400)

    def test_oversized_request_rejected_before_reading(self):
        self.assertEqual(self.request("/api/parse", b"", {"Content-Length": "1048577"})[0], 413)

    def test_unknown_route(self):
        self.assertEqual(self.request("/api/unknown", b"{}")[0], 404)
