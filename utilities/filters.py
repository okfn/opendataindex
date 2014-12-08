"""Custom Jinja filters."""


import operator
import json
import jinja2
import urlize
import markdown as mdlib
import natsort as natsortlib

md = mdlib.Markdown(extensions=[urlize.UrlizeExtension()])

operators = {
    '==': operator.eq,
    '!=': operator.ne,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
    'is': operator.is_,
    'is_not': operator.is_not
}


def markdown(content):
    """Parse `content` as markdown."""
    return jinja2.Markup(md.convert(content))


def where(iterable, key, value, op='=='):
    """Filter `iterable` of dicts on `key` where `key` `op` `value`"""
    operator_func = operators[op]
    return [o for o in iterable if operator_func(o[key], value)]


def natsort(iterable, attribute=None, reverse=False):
    """Like sort, but, all natural. For us, sorts strings as numbers."""
    _key = operator.itemgetter(attribute)
    return natsortlib.natsorted(iterable, key=_key, reverse=reverse)


def tojson(content):
    """Parse content as JSON. Does not handle errors."""
    return json.dumps(content)
