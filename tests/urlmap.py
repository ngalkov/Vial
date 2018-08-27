"""URL to view mapping"""


urlmap = [
    (r"^/$", "viewA"),
    (r"^/some_path/(?P<id>\d+)$", "viewB"),
    (r"^/(?P<param>\w+)/(?P<id>\d+)$", "viewC"),
]
