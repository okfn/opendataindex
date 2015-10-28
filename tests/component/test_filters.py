import unittest
from importlib import import_module
component = import_module('utilities.filters')


class SelectTest(unittest.TestCase):

    # Actions

    def test(self):
        func = component.search
        item1 = {'dataset': 'transport', 'place': 'au', 'year': '2015'}
        item2 = {'dataset': 'transport', 'place': 'gb', 'year': '2014'}
        items = [item1, item2]
        self.assertEqual(func(items, 'entries', dataset='transport'), items)
        self.assertEqual(func(items, 'entries', place='au'), [item1])
        self.assertEqual(func(items, 'entries', dataset='transport', year='2014'), [item2])
        self.assertEqual(func(items, 'entries', dataset='transport', year='2015'), [item1])
        self.assertEqual(func(items, 'entries', dataset='budget'), [])
