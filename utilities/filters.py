"""Custom Jinja filters."""


import sys
import operator
import json
import jinja2
import hashlib
import mdx_urlize as urlize
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


markdown_cache = {}
def markdown(content):
    """Parse `content` as markdown."""
    hash = hashlib.sha256(content.encode('ascii', 'replace')).hexdigest()
    if hash not in markdown_cache:
        markdown_cache[hash] = jinja2.Markup(md.convert(content))
    return markdown_cache[hash]


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


def debug(value):
    print(value)
    return ''


search_cache = {}
def search(items, namespace, **conditions):
    """Return new filtered list.

    Functions use cache to store indexed items.
    First time we index items using conditions,
    then we use indexed items to make fast searches.
    """
    # Caclculate outer hash
    outer_keys = sorted(conditions.keys())
    # It's like `<id>-place-year`
    outer_hash = '-'.join([namespace] + outer_keys)

    # Calculate inner hash
    inner_keys = []
    for outer_key in outer_keys:
         inner_keys.append(conditions[outer_key])
    # It's like `au-2015`
    inner_hash = '-'.join(inner_keys)

    # Prepare indexed items
    if outer_hash not in search_cache:
        search_cache[outer_hash] = {}
        for item in items:
            item_keys = []
            for outer_key in outer_keys:
                item_keys.append(item[outer_key])
            # It's like `gb-2014`
            item_hash = '-'.join(item_keys)
            store = search_cache[outer_hash].setdefault(item_hash, [])
            store.append(item)

    return list(search_cache[outer_hash].get(inner_hash, []))


def first_or_default(items, default):
    """Return first item or default if items is empty.
    """
    if items:
        return items[0]
    return default
