import unittest
from unittest.mock import Mock
from vial import *

class TestResponse(unittest.TestCase):
    def test_init(self):
        response = Response(body="test body", status_line="test_status")
        self.assertEqual(response.body, ["test body"])
        self.assertEqual(response.status_line, "test_status")
        self.assertListEqual(response.headers, [])
        self.assertEqual(response.encoding, "utf-8")
        # ensure body is iterable
        import collections
        self.assertIsInstance(Response().body, collections.Iterable)
        self.assertIsInstance(Response(body="test").body, collections.Iterable)
        self.assertIsInstance(Response(body=["a", "b", "c"]).body, collections.Iterable)

    def test_add_header(self):
        response = Response(body="test body", status_line="test_status")
        response.add_header("header_name", "header_value")
        self.assertIn(("header_name", "header_value"), response.headers)

    def test_call_ok(self):
        # ensure start_response called
        mock_start_response = Mock()
        response = Response(body=["line1", "строка2"], status_line="000 test_status")
        response("environ", mock_start_response)
        mock_start_response.assert_called_with(
            "000 test_status",
            [('Content-Length', '18'), ('Content-Type', 'text/html; charset = utf-8')]
        )
        # test body returned
        returned = response("environ", mock_start_response)
        self.assertListEqual(returned, [b"line1", b'\xd1\x81\xd1\x82\xd1\x80\xd0\xbe\xd0\xba\xd0\xb02'])

    def test_call_empty_body(self):
        mock_start_response = Mock()
        response = Response(status_line="200 OK")
        returned = response("environ", mock_start_response)
        mock_start_response.assert_called_with("200 OK", [('Content-Length', '0')])
        self.assertListEqual(returned, [])

    def test_call_empty_status_line(self):
        mock_start_response = Mock()
        response = Response(body=["line1", "строка2"])
        response("environ", mock_start_response)
        mock_start_response.assert_called_with("500 Internal Server Error", [('Content-Length', '0')])

