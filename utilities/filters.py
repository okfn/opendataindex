"""Custom Jinja filters."""


import operator
import json
import jinja2
import markdown as mdlib
import natsort as natsortlib


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

    return jinja2.Markup(mdlib.markdown(content))


def where(iterable, key, value, op='=='):
    """This is a POC that expects an iterable of dicts only.

    Filter `iterable` on `key` where `key` `op` `value`

    """

    operator_func = operators[op]
    return [o for o in iterable if operator_func(o[key], value)]


def natsort(iterable, attribute=None, reverse=False):
    """Like sort, but, all natural. For us, sorts strings as numbers."""

    return natsortlib.natsorted(iterable, key=operator.itemgetter(attribute),
                                reverse=reverse)


def tojson(content):
    """."""

    return json.dumps(content)
