"""Custom Jinja filters."""


import jinja2
import markdown as mdlib


def markdown(content):
    """Parse `content` as markdown."""

    return jinja2.Markup(mdlib.markdown(content))


def where(iterable, key, value):
    """This is a POC that expects an iterable of dicts only.

    Filter `iterable` on `key` where `key` is `value`

    """

    return [o for o in iterable if o[key] == value]
