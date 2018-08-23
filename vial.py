"""The Python WSGI picoframework"""

import os
import re
import html
from string import Template


ENCODING = "utf-8"
TEMPLATE_DIR = "./template"


class Response:
    # Response instance is a WSGI app itself. It can be useful for middleware.
    def __init__(self, body=None, status_line=None):
        # self.body must be iterable
        if not body:
            self.body = []
        elif isinstance(body, str):
            self.body = [body]
        else:
            self.body = list(body)
        self.status_line = status_line
        self.headers = []
        self.encoding = ENCODING

    def add_header(self, name, value):
        self.headers.append((name, value))

    def __call__(self, environ, start_response):
        if not self.status_line:
            self.status_line = "500 Internal Server Error"
            self.body = []
        # WSGI app must return byte string
        encoded_body = [item.encode(self.encoding) for item in self.body]
        encoded_body_length = sum(map(len, encoded_body))
        self.add_header("Content-Length", str(encoded_body_length))
        if encoded_body_length > 0:
            self.add_header("Content-Type", "text/html; charset = %s" % self.encoding)
        start_response(self.status_line, self.headers)
        return encoded_body


class Vial:
    def __init__(self):
        from urlmap import urlmap
        self.urlmap = urlmap

    def wsgi_app(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        view = self.dispath_request(path_info)
        response = view(environ)
        return response(environ, start_response)

    def dispath_request(self, path_info):
        for pattern, view in self.urlmap:
            if re.search(pattern, path_info):
                return view
        return self.not_found

    def not_found(self, environ):
        return Response("Not found.", "404 Not Found")

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def render_template(template_file: str, context: dict) -> str:
    """Replace placeholders in template_file accordingly to context. &, <, > will be escaped to HTML-safe sequences"""
    template_path = os.path.join(TEMPLATE_DIR, template_file)
    with open(template_path, encoding=ENCODING) as fp:
        template_content = fp.read()
    template = Template(template_content)
    escaped_context = {key: html.escape(value) for key,value in context.items()}
    return template.substitute(escaped_context)