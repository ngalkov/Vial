"""The Python WSGI picoframework"""

import re

from urlmap import urlmap


class Vial:
    def __init__(self):
        pass
        
    def wsgi_app(self, environ, start_response):
        path_info = environ.get('PATH_INFO', '')
        view = self.dispath_request(path_info)
        response = view(environ)
        start_response('200 OK', [('content-type', 'text/html')])
        return [response]

    def dispath_request(self, path_info):
        for pattern, view in urlmap:
            if re.search(pattern, path_info):
                return view
        return self.not_found

    def not_found(self, environ):
        return b'Not found.'

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)
