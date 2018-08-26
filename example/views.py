from vial import Response, render_template


def index(environ):
    content = render_template("index.html", {})
    return Response(content, "200 OK")


def hello(environ):
    content = render_template("hello.html", {})
    return Response(content, "200 OK")


def item(environ, item_id):
    content = render_template("item.html", {"item_id": item_id})
    return Response(content, "200 OK")

def logo(environ):
    content = render_template("logo.html", {})
    return Response(content, "200 OK")

