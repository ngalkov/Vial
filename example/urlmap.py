"""URL to view mapping"""


urlmap = [
    (r"^/$", "index"),
    (r"^/item/(?P<item_id>\d+)$", "item"),
]
