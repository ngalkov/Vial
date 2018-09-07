"""The Python WSGI picoframework"""

import os
import re
import html
from string import Template
from enum import Enum


ENCODING = "utf-8"
TEMPLATE_DIR = "./templates"
STATIC_DIR = "./static"
STATIC_URL = "/static"


class Status(Enum):
    OK = 200
    BAD_REQUEST = 400
    FORBIDDEN = 403
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


STATUS_LINES = {
    Status.OK: "200 OK",
    Status.BAD_REQUEST: "400 Bad Request",
    Status.FORBIDDEN: "403 Forbidden",
    Status.NOT_FOUND: "404 Not Found",
    Status.INTERNAL_ERROR: "500 Internal Server Error",
}

MIME_TYPE = {
    ".txt": "text/plain",
    ".text": "text/plain",
    ".htm": "text/html",
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".swf": "application/x-shockwave-flash"
}


class Response:
    """The Response object implements WSGI Response.

    The Response instance will start a valid WSGI response when called with the environ and start response
    callable. The Response instance is a WSGI app itself - it can be useful for middleware.
    """

    def __init__(self, body=None, status_code=None, content_type="text/html", encoding="utf-8"):
        # self.body must be iterable
        if not body:
            self.body = []
        elif isinstance(body, str) or isinstance(body, bytes):
            self.body = [body]
        else:
            self.body = list(body)
        self.status_code = status_code
        self.content_type = content_type
        self.encoding = encoding
        self.headers = []

    def add_header(self, name, value):
        self.headers.append((name, value))

    def __call__(self, environ, start_response):
        if not self.status_code:
            self.status_code = Status.INTERNAL_ERROR
            self.body = []
        # WSGI app must return byte string
        encoded_body = []
        for item in self.body:
            if isinstance(item, str):
                encoded_body.append(item.encode(self.encoding or ENCODING))  # self.encoding can be None
            else:
                encoded_body.append(item)
        encoded_body_length = sum(map(len, encoded_body))
        content_type_header = self.content_type or "application/octet-stream"  # self.content_type can be None
        if self.encoding:
            content_type_header += "; charset = %s" % self.encoding
        self.add_header("Content-Type", content_type_header)
        self.add_header("Content-Length", str(encoded_body_length))
        start_response(STATUS_LINES[self.status_code], self.headers)
        return encoded_body


class Vial:
    """The Vial object implements a WSGI application."""

    def __init__(self):
        import views
        from urlmap import urlmap
        self.views = views
        self.urlmap = urlmap

    def not_found(self, environ):
        return Response(body=None, status_code=Status.NOT_FOUND, content_type=None, encoding=None)

    def static_file(self, environ, static_file_path):
        if not os.path.isfile(static_file_path):
            return self.not_found(environ)
        try:
            with open(static_file_path, "rb") as fp:
                static_file_content = fp.read()
        except OSError:
            return Response(None, Status.INTERNAL_ERROR)
        return Response(
            body=static_file_content,
            status_code=Status.OK,
            content_type=get_mime_type(static_file_path),
            encoding=None
        )

    def wsgi_app(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        if path_info.startswith(STATIC_URL):
            static_file_path = os.path.join(STATIC_DIR, path_info.replace(STATIC_URL, "", 1).lstrip("/"))
            response = self.static_file(environ, static_file_path)
            return response(environ, start_response)
        view_name, view_kwargs = self.dispath_url(path_info)
        if not view_name:
            response = self.not_found(environ)
            return response(environ, start_response)
        view = getattr(self.views, view_name)
        if view_kwargs:
            response = view(environ, **view_kwargs)
        else:
            response = view(environ)
        return response(environ, start_response)

    def dispath_url(self, path_info):
        for url_pattern, view_name in self.urlmap:
            url_match = re.search(url_pattern, path_info)
            if url_match:
                return view_name, url_match.groupdict()
        return None, {}

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def render_template(template_file: str, context: dict) -> str:
    """Replace placeholders in template_file accordingly to context. &, <, > will be escaped to HTML-safe sequences"""
    template_path = os.path.join(TEMPLATE_DIR, template_file)
    with open(template_path, encoding=ENCODING) as fp:
        template_content = fp.read()
    template = Template(template_content)
    escaped_context = {key: html.escape(value) for key, value in context.items()}
    return template.substitute(escaped_context)


def get_mime_type(path):
    ext = os.path.splitext(path)[1]
    return MIME_TYPE.get(ext, "application/octet-stream")
