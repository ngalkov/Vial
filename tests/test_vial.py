import unittest
from unittest.mock import Mock, patch
from vial import *


class TestResponse(unittest.TestCase):
    def test_init(self):
        response = Response(body="test body", status_line="test_status")
        self.assertEqual(response.body, ["test body"])
        self.assertEqual(response.status_line, "test_status")
        self.assertListEqual(response.headers, [])
        self.assertEqual(response.content_type, "text/html")
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
            [('Content-Type', 'text/html; charset = utf-8'), ('Content-Length', '18')]
        )
        # test returned value
        self.assertListEqual(returned, [b"line1", b'\xd1\x81\xd1\x82\xd1\x80\xd0\xbe\xd0\xba\xd0\xb02'])

    def test_call_empty_body(self):
        mock_start_response = Mock()
        response = Response(status_line="200 OK")
        returned = response("environ", mock_start_response)
        # ensure start_response called
        mock_start_response.assert_called_with(
            "200 OK",
            [('Content-Type', 'text/html; charset = utf-8'), ('Content-Length', '0')]
        )
        # test returned value
        self.assertListEqual(returned, [])

    def test_call_empty_status_line(self):
        mock_start_response = Mock()
        response = Response(body=["line1", "строка2"])
        returned = response("environ", mock_start_response)
        # ensure start_response called
        mock_start_response.assert_called_with(
            "500 Internal Server Error",
            [('Content-Type', 'text/html; charset = utf-8'), ('Content-Length', '0')]
        )
        # test returned value
        self.assertListEqual(returned, [])

class TestVial(unittest.TestCase):
    def test_dispath_request(self):
        app = Vial()
        self.assertTupleEqual(app.dispath_url("/"), ("viewA", {}))
        self.assertTupleEqual(app.dispath_url("/some_path/123"), ("viewB", {"id": "123"}))
        self.assertTupleEqual(app.dispath_url("/value/123"), ("viewC", {"param": "value", "id": "123"}))
        self.assertTupleEqual(app.dispath_url("/bad/path"), (None, {}))

    def test_static_file(self):
        app = Vial()
        mock_environ = {}
        mock_start_response = Mock()
        # OK
        response = app.static_file(mock_environ, "./static/static_file_text.txt")
        returned = response(mock_environ, mock_start_response)
        mock_start_response.assert_called_with(
            '200 OK',
            [('Content-Type', 'text/plain'), ('Content-Length', '25')]
        )
        self.assertListEqual(returned, [b'Test static files serving'])
        # Bad file name
        response = app.static_file(mock_environ, "./static/bad_file_name.txt")
        returned = response(mock_environ, mock_start_response)
        mock_start_response.assert_called_with(
            "404 Not Found",
            [('Content-Type', 'application/octet-stream'), ('Content-Length', '0')]
        )


    def test_wsgi_app(self):
        app = Vial()

        # simple url (without parameters)
        mock_environ = {"PATH_INFO": "/"}
        mock_start_response = Mock()
        returned = app(mock_environ, mock_start_response)
        mock_start_response.assert_called_with(
            '200 OK',
            [('Content-Type', 'text/html; charset = utf-8'), ('Content-Length', '5')]
        )
        self.assertListEqual(returned, [b'viewA'])

        # url with parameters)
        mock_environ = {"PATH_INFO": "/value/123"}
        mock_start_response = Mock()
        returned = app(mock_environ, mock_start_response)
        mock_start_response.assert_called_with(
            '200 OK',
            [('Content-Type', 'text/html; charset = utf-8'), ('Content-Length', '17')]
        )
        self.assertListEqual(returned, [b'viewC: value, 123'])

        # bad url
        mock_environ = {"PATH_INFO": "/bad/url"}
        mock_start_response = Mock()
        returned = app(mock_environ, mock_start_response)
        mock_start_response.assert_called_with(
            '404 Not Found',
            [('Content-Type', 'application/octet-stream'), ('Content-Length', '0')]
        )
        self.assertListEqual(returned, [])

        # static url OK
        mock_environ = {"PATH_INFO": "/static/static_file_text.txt"}
        mock_start_response = Mock()
        returned = app(mock_environ, mock_start_response)
        mock_start_response.assert_called_with(
            '200 OK',
            [('Content-Type', 'text/plain'), ('Content-Length', '25')]
        )
        self.assertListEqual(returned, [b'Test static files serving'])

        # bad static url
        mock_environ = {"PATH_INFO": "/ststic/bad/url"}
        mock_start_response = Mock()
        returned = app(mock_environ, mock_start_response)
        mock_start_response.assert_called_with(
            '404 Not Found',
            [('Content-Type', 'application/octet-stream'), ('Content-Length', '0')]
        )

    def test_render_template_ok(self):
        # OK
        rendered = render_template(template_file="template_test.html",
                                   context={"title": "Header", "content": "Содержание", "escaped": "<tag&>"})
        self.assertEqual(rendered.replace("\r\n", "\n"),
                         "<h1>Header</h1>\n<p>Содержание</p>\n<p>&lt;tag&amp;&gt;</p>")
        # Fail
        self.assertRaises(OSError, render_template, "bad_filename.html",
                          {"title": "Header", "content": "Содержание", "escaped": "<tag&>"})
        self.assertRaises(KeyError, render_template, "template_test.html", {})


if __name__ == '__main__':
    unittest.main()
