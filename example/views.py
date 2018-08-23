from vial import Response


def index(environ):
    msg = 'Hi!<br> This is the main page.'
    return Response(msg, "200 OK")
