import unittest
from unittest.mock import Mock, patch
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
        mock_start_response = Mock()
        response = Response(body=["line1", "строка2"], status_line="000 test_status")
        returned = response("environ", mock_start_response)
        # ensure start_response called
        mock_start_response.assert_called_with(
            "000 test_status",
            [('Content-Length', '18'), ('Content-Type', 'text/html; charset = utf-8')]
        )
        # test returned value
        self.assertListEqual(returned, [b"line1", b'\xd1\x81\xd1\x82\xd1\x80\xd0\xbe\xd0\xba\xd0\xb02'])

    def test_call_empty_body(self):
        mock_start_response = Mock()
        response = Response(status_line="200 OK")
        returned = response("environ", mock_start_response)
        # ensure start_response called
        mock_start_response.assert_called_with("200 OK", [('Content-Length', '0')])
        # test returned value
        self.assertListEqual(returned, [])

    def test_call_empty_status_line(self):
        mock_start_response = Mock()
        response = Response(body=["line1", "строка2"])
        returned = response("environ", mock_start_response)
        # ensure start_response called
        mock_start_response.assert_called_with("500 Internal Server Error", [('Content-Length', '0')])
        # test returned value
        self.assertListEqual(returned, [])

class TestVial(unittest.TestCase):
    def test_dispath_request(self):
        app = Vial()
        self.assertTupleEqual(app.dispath_url("/"), ("viewA", {}))
        self.assertTupleEqual(app.dispath_url("/some_path/123"), ("viewB", {"id": "123"}))
        self.assertTupleEqual(app.dispath_url("/value/123"), ("viewC", {"param": "value", "id": "123"}))
        self.assertTupleEqual(app.dispath_url("/bad/path"), (None, {}))

    def test_wsgi_app(self):  # TODO"
        app = Vial()
        mock_environ = {"PATH_INFO": "/value/123"}
        mock_start_response = Mock()
        returned = app(mock_environ, mock_start_response)
        mock_start_response.assert_called_with(
            '200 OK',
            [('Content-Length', '17'), ('Content-Type', 'text/html; charset = utf-8')]
        )
        self.assertListEqual(returned, [b'viewC: value, 123'])

    def test_render_template_ok(self):
        rendered = render_template(template_file="template_test.html",
                                   context={"title": "Header", "content": "Содержание", "escaped": "<tag&>"})
        self.assertEqual(rendered.replace("\r\n", "\n"),
                         "<h1>Header</h1>\n<p>Содержание</p>\n<p>&lt;tag&amp;&gt;</p>")

    def test_render_template_fail(self):
        self.assertRaises(OSError, render_template, "bad_filename.html",
                          {"title": "Header", "content": "Содержание", "escaped": "<tag&>"})
        self.assertRaises(KeyError, render_template, "template_test.html", {})


if __name__ == '__main__':
    unittest.main()
