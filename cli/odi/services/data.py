import os
import requests
import unicodecsv as csv
from collections import OrderedDict
from . import config
config = config.get_config()
cache = {}


def load_items(entity, year=None):
    """Load json results from url.
    """
    if year is None:
        year = config.ODI['current_year']
    hash = '-'.join([entity, year])
    if hash not in cache:
        db = config.ODI['database'][entity]
        url = db.format(year=year)
        res = requests.get(url)
        json = res.json()
        items = json['results']
        cache[hash] = items
    return cache[hash]


def load_history(entity):
    """Load entity data by years.
    """
    data = {}
    for year in config.ODI['years']:
        # Load data for year as list
        items = load_items(entity, year=year)
        # Index data by id, list to dict conversion
        data[year] = OrderedDict()
        for item in items:
            data[year][item['id']] = item
    return data


def add_prev_years(history, fieldnames, items):
    """Add fields with prev year values of rank and score.
    """
    for item in items:
        for year in config.ODI['years']:
            if year == config.ODI['current_year']:
                continue
            # Rank and score
            for param in ['rank', 'score']:
                key = '{param}_{year}'.format(param=param, year=year)
                try:
                    value = history[year][item['id']][param]
                except KeyError:
                    value = ''
                if key not in fieldnames:
                    fieldnames.append(key)
                item[key] = value


def save_items(entity, fieldnames, items):
    """Save list of dicts to csv with fieldnames.
    """
    path = os.path.join(config.DATASTORE['location'], '%s.csv' % entity)
    with open(path, 'w') as file:
        writer = csv.DictWriter(
            file, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for item in items:
            writer.writerow(item)
