from vial import Response


def index(environ):
    msg = 'Hi!<br> This is the main page.'
    return Response(msg, "200 OK")


def item(environ, item_id):
    msg = 'Item # %s' % item_id
    return Response(msg, "200 OK")
