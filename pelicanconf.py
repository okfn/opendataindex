#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

UTILITIES = os.path.join(PROJECT_ROOT, 'utilities')
sys.path.insert(1, UTILITIES)

import filters


AUTHOR = u'Open Knowledge'
SITENAME = u'Open Data Index'
SITEURL = ''

PATH = 'content'

TIMEZONE = 'Europe/Paris'

DEFAULT_LANG = u'en'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'

AUTHOR_SAVE_AS = False
AUTHORS_SAVE_AS = False
CATEGORY_SAVE_AS = False
CATEGORIES_SAVE_AS = False
TAG_SAVE_AS = False
TAGS_SAVE_AS = False
ARCHIVES_SAVE_AS = False

PLUGIN_PATHS = [os.path.join(PROJECT_ROOT, 'plugins')]
PLUGINS = ['datastore',]

THEME = os.path.join(PROJECT_ROOT, 'themes', 'okfn')
THEME_STATIC_DIR = 'static'

# Our DATASTORE PLUGIN settings
DATASTORE = {
    'location': os.path.join(PROJECT_ROOT, 'data'),
    'formats': ['.csv'],
    'true_strings': ['TRUE', 'True', 'true'],  # 'YES', 'Yes', 'yes'
    'false_strings': ['FALSE', 'False', 'false'],  # 'NO', 'No', 'no'
    'none_strings': ['NULL', 'Null', 'null', 'NONE', 'None', 'none',
                     'NIL', 'Nil', 'nil', '-', 'NaN', 'N/A', 'n/a', '']
}

# OPEN KNOWLEDGE SETTINGS
OK = {
    'ribbon': False
}

# OPEN DATA INDEX SETTINGS
ODI = {
    'years': ['2014', '2013'],
    'current_year': '2014',
    'na': 'n/a',
    'email': 'index@okfn.org',
    'description': 'The Open Data Index assesses the state of open government data around the world.',
    'twitter': '',
    'repo': 'https://github.com/okfn/opendataindex',
    'author': {
        'name': AUTHOR,
        'url': 'https://okfn.org/'
    },
    'googleanalytics': '',
    'mailinglist': ''
}



JINJA_EXTENSIONS = [
  'jinja2.ext.i18n',
  'jinja2.ext.do',
  'jinja2.ext.with_',
  'jinja2.ext.loopcontrols'
]

JINJA_FILTERS = {
  'where': filters.where,
  'markdown': filters.markdown
}
