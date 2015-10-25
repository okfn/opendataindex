import os
import operator
import requests
import unicodecsv as csv
from collections import OrderedDict
from . import config
config = config.get_config()
cache = {}


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
        filter_items(entity, items, year)
        cache[hash] = items
    return cache[hash]


def filter_items(entity, items, year):
    """Mutate items against filter based on config.
    """
    for filt in ['include', 'exclude']:
        for item in list(items):
            skip = True
            keep = filt == 'exclude'
            oper = operator.and_ if filt == 'exclude' else operator.or_
            for filt_entity, filt_list in config.ODI[filt].items():
                fieldname = filt_entity[:-1]  # like places -> place
                if entity == filt_entity:
                    fieldname = 'id'
                if fieldname not in item:
                    continue
                item_hash = '-'.join([item[fieldname], year])  # like gb-2015
                for filt_hash in filt_list:
                    filt_keep = item_hash.startswith(filt_hash)
                    if filt == 'exclude':
                        filt_keep = not filt_keep
                    keep = oper(keep, filt_keep)
                    skip = False
            if not skip and not keep:  # Remove item
                try:
                    items.remove(item)
                except ValueError:
                    pass
    if not len(items):  # Check it's not empty
        raise ValueError(
            'Filter for `{entity}-{year}` is to tight. '
            'There are no items found in the database.'.
            format(entity=entity, year=year))


def add_prev_years_to_items(history, fieldnames, items):
    """Mutate items adding fields with prev year values of rank and score.
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


def sort_and_add_rank_to_items(items):
    """Mutate items sorting it and adding rank based on score.
    """
    items.sort(key=lambda item: item['score'], reverse=True)
    current_rank = None
    current_score = None
    for num, item in enumerate(items):
        if current_score != item['score']:
            current_rank = num + 1
            current_score = item['score']
        item['rank'] = current_rank


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
