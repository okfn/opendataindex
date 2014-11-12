#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals
import os
import sys
sys.path.append(os.curdir)
from config_default import *


RELATIVE_URLS = False
SITEURL = 'http://staging.index.okfn.org'
DELETE_OUTPUT_DIRECTORY = True

ODI['scheme'] = u'http://'
ODI['domain'] = u'staging.index.okfn.org'

SITEURL = u'{0}{1}'.format(ODI['scheme'], ODI['domain'])
