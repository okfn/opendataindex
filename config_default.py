#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os
import sys
import datetime


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

UTILITIES = os.path.join(PROJECT_ROOT, 'utilities')
sys.path.insert(1, UTILITIES)

import filters

LOAD_CONTENT_CACHE = False
AUTORELOAD_IGNORE_CACHE = True

AUTHOR = u'Open Knowledge'
SITENAME = u'Open Data Index'
SITEURL = u''

STATIC_PATHS = ['extra/CNAME']
EXTRA_PATH_METADATA = {'extra/CNAME': {'path': 'CNAME'},}
PATH = 'content'
OUTPUT_PATH = 'output'

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
PLUGINS = ['datastore', 'datastore_api', 'datastore_assets']

THEME = os.path.join(PROJECT_ROOT, 'themes', 'odi')
THEME_STATIC_DIR = 'static'
THEME_STATIC_PATH = os.path.join(THEME, THEME_STATIC_DIR)

DISPLAY_DATE_FORMAT = '%Y-%m-%d'
DISPLAY_TIME_FORMAT = '%H:%M:%S'
DISPLAY_DATETIME_FORMAT = '{0}T{1}'.format(DISPLAY_DATE_FORMAT,
                                           DISPLAY_TIME_FORMAT)

TIMESTAMP = datetime.datetime.now().strftime(DISPLAY_DATE_FORMAT)

# Our DATASTORE PLUGIN settings
DATASTORE = {
    'location': os.path.join(PROJECT_ROOT, 'data'),
    'formats': ['.csv'],
    'true_strings': ['TRUE', 'True', 'true'],
    'false_strings': ['FALSE', 'False', 'false'],
    'none_strings': ['NULL', 'Null', 'null', 'NONE', 'None', 'none',
                     'NIL', 'Nil', 'nil', '-', 'NaN', 'N/A', 'n/a', ''],
    'api': { # settings for the datastore_api plugin
        'base': 'api', # directory relative to `output`
        'formats': ['json', 'csv'], # output API in these formats
        'filters': {
            # Key must match a datastore file name.
            # Values must match headers in that file.
            'entries': ['year'],
            'datasets': ['category']
            #'places': ['region']
        },
        'exclude': [] # datastore files to exclude from API (by name of type)
    },
    'assets': {
        'location': 'downloads'
    }
}

# OPEN KNOWLEDGE SETTINGS
OK = {
    'ribbon': False
}

# OPEN DATA INDEX SETTINGS
ODI = {
    'survey': {
      'name': u'Open Data Index Survey',
      'domain': u'http://global.census.okfn.org/',
      'submit_route': u'submit/'
    },
    'sponsor': {
      'name': u'Open Knowledge',
      'domain': u'https://okfn.org/',
    },
    'years': [u'2014', u'2013'],
    'current_year': u'2014',
    'na': u'n/a',
    'email': u'index@okfn.org',
    'description': u'The Open Data Index assesses the state of open government data around the world.',
    'twitter': '',
    'repo': u'https://github.com/okfn/opendataindex',
    'author': {
        'name': AUTHOR,
        'url': u'https://okfn.org/'
    },
    'googleanalytics': u'',
    'mailinglist': u''
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
