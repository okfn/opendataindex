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
DEFAULT_LANG = u'en'
PATH = 'content'
STATIC_PATHS = ['extra/CNAME', 'data']
EXTRA_PATH_METADATA = {
  'extra/CNAME': {'path': 'CNAME'},
}
OUTPUT_PATH = 'output'
TIMEZONE = 'UTC'
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
LINKS = (('', ''),)
SOCIAL = (('', ''),)
DEFAULT_PAGINATION = False
ARTICLE_URL = 'stories/{date:%Y}/{slug}/'
ARTICLE_SAVE_AS = 'stories/{date:%Y}/{slug}/index.html'
INDEX_SAVE_AS = 'stories/index.html'
PAGE_URL = '{slug}/'
PAGE_SAVE_AS = '{slug}/index.html'
AUTHOR_SAVE_AS = False
AUTHORS_SAVE_AS = False
CATEGORY_URL = 'stories/{slug}/'
CATEGORY_SAVE_AS = 'stories/{slug}/index.html'
#CATEGORY_SAVE_AS = False
#CATEGORIES_SAVE_AS = False
TAG_SAVE_AS = False
TAGS_SAVE_AS = False
ARCHIVES_SAVE_AS = False
THEME = os.path.join(PROJECT_ROOT, 'themes', 'odi')
THEME_STATIC_DIR = 'static'
THEME_STATIC_PATH = os.path.join(THEME, THEME_STATIC_DIR)
DISPLAY_DATE_FORMAT = '%Y-%m-%d'
DISPLAY_TIME_FORMAT = '%H:%M:%S'
DISPLAY_DATETIME_FORMAT = '{0}T{1}'.format(DISPLAY_DATE_FORMAT,
                                           DISPLAY_TIME_FORMAT)
TIMESTAMP = datetime.datetime.now().strftime(DISPLAY_DATE_FORMAT)
SUMMARY_MAX_LENGTH = 25
JINJA_EXTENSIONS = [
  'jinja2.ext.i18n',
  'jinja2.ext.do',
  'jinja2.ext.with_',
  'jinja2.ext.loopcontrols'
]
JINJA_FILTERS = {
  'where': filters.where,
  'markdown': filters.markdown,
  'natsort': filters.natsort,
  'tojson': filters.tojson
}
PLUGIN_PATHS = [os.path.join(PROJECT_ROOT, 'plugins')]
PLUGINS = [
  'datastore',
  'datastore_api',
  'datastore_assets',
  'i18n_subsites',
  'pelican_alias'
]

# DATASTORE PLUGIN CONFIGURATION
DATASTORE = {
    'location': os.path.join(PROJECT_ROOT, 'content', 'data'),
    'formats': ['.csv'],
    'intrafield_delimiter': '~*',
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

OK = {
    'ribbon': True
}

# OPEN DATA INDEX CONFIGURATION
ODI = {
    'scheme': u'',
    'domain': u'',
    'production_domain': u'index.okfn.org',
    'survey': {
      'name': u'Open Data Index Survey',
      'domain': u'http://global.census.okfn.org/',
      'submit_route': u'submit/'
    },
    'sponsor': {
      'name': u'Open Knowledge',
      'domain': u'https://okfn.org/',
    },
    'analytics': {
      'google': u''
    },
    'stories': {
      'email': 'index@okfn.org'
    },
    'press': {
      'email': 'press@okfn.org'
    },
    'years': [u'2015', u'2014', u'2013'],
    'current_year': u'2015',
    'previous_year': u'2014',
    'na': u'n/a',
    'email': u'index@okfn.org',
    'description': u'The Global Open Data Index assesses the state of open government data around the world.',
    'keywords': 'Open Government, Open Data, Government Transparency, Open Knowledge',
    'twitter': '',
    'repo': u'https://github.com/okfn/opendataindex',
    'author': {
        'name': AUTHOR,
        'url': u'https://okfn.org/'
    },
    'mailinglist': u'',
    'languages': ['en', 'es'],
    'test_path': 'tests',
    'tmp_path': 'tmp',
    'content_path': PATH,
    'output_path': OUTPUT_PATH,
    'trans_path': 'themes/odi/translations',
    'deploy_remote': 'upstream',
    'database': 'endpoint}.json',
    'database': {
        'entries': 'http://global.census.okfn.org/api/entries/{year}.cascade.json',
        'places': 'http://global.census.okfn.org/api/places/score/{year}.cascade.json',
        'datasets': 'http://global.census.okfn.org/api/datasets/score/{year}.cascade.json',
        'questions': 'http://global.census.okfn.org/api/questions.json',
    },
    'limited': {
        'places': ['au'],
        'datasets': ['timetables']
    },
    'forms': {
      'download': {
        'url': 'https://docs.google.com/forms/d/1fEJxaJdOI9SxicgS3INwrgtGLK43qLTPpFiQ-e2ISm0/viewform?embedded=true',
        'width': '560',
        'height': '720'

      }
    }
}

SITEURL = u'{0}{1}'.format(ODI['scheme'], ODI['domain'])

# If `config_instance` exists, load it for instance-specific configuration.
# See `config_instance.example` to get started.
try:
  from config_instance import *
except ImportError:
  pass
