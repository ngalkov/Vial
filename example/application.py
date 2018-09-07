"""The main WSGI application."""

import logging

from vial import Vial

app = Vial()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    from wsgiref.simple_server import make_server
    with make_server('', 8000, app) as httpd:
        logging.info("Serving on port 8000...")
        httpd.serve_forever()
