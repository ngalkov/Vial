"""URL to view mapping"""


urlmap = [
    (r"^/$", "index"),
    (r"^/hello$", "hello"),
    (r"^/item/(?P<item_id>\d+)$", "item"),
    (r"^/logo$", "logo"),
]
