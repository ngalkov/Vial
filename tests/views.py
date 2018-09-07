from vial import Response, Status


def viewA(environ):
    return Response("viewA", Status.OK)


def viewB(environ, id):
    return Response("viewB: %s" % id, Status.OK)


def viewC(environ, param, id):
    return Response("viewC: %s, %s" % (param, id), Status.OK)
