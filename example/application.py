"""The main WSGI application."""

from vial import Vial

app = Vial()

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    with make_server('', 8000, app) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()