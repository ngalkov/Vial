from vial import Response


def viewA(environ):
    return Response("viewA", "200 OK")


def viewB(environ, id):
    return Response("viewB: %s" % id, "200 OK")


def viewC(environ, param, id):
    return Response("viewC: %s, %s" % (param, id), "200 OK")
