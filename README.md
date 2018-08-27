# Vial
The Python WSGI pico-framework

## Description
Vial is yet another Python WSGI framework created for an educational purpose. It has routing system, that maps urls to function-based views and templating system, based on standard python Template class.  
Vial parses url, extracts parameters from url (if necessary), selects an appropriate view, renders html page, based on a specified template and returns it. See the relevant sections for more details. 

## Installation
Vial is distributed as a single file module and does not depend on any external libraries. Just put vial.py into your project directory or anywhere on PYTHONPATH.

## Quickstart: “Hello World” application
Create project directory like this:  
```
/hello_world
    /static
    /templates
    hello.py
    urlmap.py
    views.py
```

hello.py:
```
from vial import Vial

application = Vial()
```

urlmap.py:
```
urlmap = [
    (r"^/$", "hello"),
]

```

views.py:
```
from vial import Response, render_template


def hello(environ):
    content = "Hello World!"
    return Response(content, "200 OK")
```
Configure your WSGI server to serve application.py. For example, to deploy aplication on HTTP port 8000 with uWSGI start it to run an HTTP server/router passing requests to your WSGI application:
```
uwsgi --http :8000 --wsgi-file hello.py
```
Alternatively, during development, you can use `wsgiref.simple_server` from Python stdlib. Edit hello.py:
```
from vial import Vial

application = Vial()

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    with make_server('', 8000, application) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()
```
and start application:
```
python -m hello
```

## Routing
Vial provides Django-like routing. Urlmap.py has the list of routes that maps url into view:
```
urlmap = [
    (r"^/$", "viewA"),
    (r"^/some_path/(?P<id>\d+)$", "viewB"),
    (r"^/(?P<param>\w+)/(?P<id>\d+)$", "viewC"),
]
```
Each route is a tuple of regular expression that mathes url and name of view that handles that url. Vial checks regular expression from top to bottom until it finds one that matches. If no one matches Vial returns 404.  
Using grouping in regex makes it possible to extract part of the url and passes it into view. For example, the url `/some_path/123` matches the second route, so "123" will be extracted and the view will be called like this: `viewB(environ, id=123)`

## Views
When Vial finds the right match for the url it calls the corresponding view: `view(environ)` or if regex defines parameters to extract from url: `view(environ, **kwargs)`.  
* `environ` is a dictionary populated by the server with CGI like variables at each request from the client.  
* `**kwargs` are keyword arguments extracted from url.  

A view is a function defined in views.py. Each view is responsible for returning a Response object containing the content for the requested page. It can use templates for rendering the content.

## Response
Each view should return an instanse of Response class. To create it call
```
Response(body=None, status_line=None, content_type="text/html", encoding="utf-8"
```
* `body` is data that the body of HTTP response from server to client should contain
* `status_line` is the status line of HTTP response from server
* `content_type`, `encoding`  - used to make `Content-Type` HTTP header

A Response also automatically add `Content-Length` HTTP header. 

## Templates
Templating system bases on standard python Template class.  
Templates are files that live in `template` folder. A template contains the static parts of the desired HTML output and placeholders with special syntax to insert dynamic content. Placeholders have the form: `$identifier`.  
To create dynamic content use render_template function:
```
from Vial import render_template

render_template(template_file, context)
```
* `template_file` is the name of temlate
* `context` is a dict maps placeholder name to its value

For example if you have `hello.html` in templates folder:
```
<p>Hello, $user</p>
```
Then `render_template("hello.html", {"user": "Bob"})` return string `<p>Hello, Bob</p>`  
Note that symbols `&, <, >` will be escaped to HTML-safe sequences

## Static files
Usually, your web server is configured to serve static files (images, java scripts, etc.), but Vial can do that as well.  
Static files should be put in a folder in your project called `static` and they will be available at `/static` url.

## Example
Simple example build with Vial is provided - see `./example` folder.

## Requirements
Python 3.6 or higher  

## Tests
A test suite is provided with a complete environment (`./tests` folder).  

