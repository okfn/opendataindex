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


def load_items(entity, year=None, exclude=True):
    """Load json results from url.
    """
    if year is None:
        year = config.ODI['current_year']
    hash = '-'.join([entity, year, str(exclude)])
    if hash not in cache:
        db = config.ODI['database'][entity]
        url = db.format(year=year)
        pld = {}
        if exclude:
            for item in ['datasets', 'places']:
                key = 'exclude_%s' % item
                try:
                    value = ','.join(config.ODI['exclude'][year][item])
                    pld[key] = value
                except Exception:
                    pass
        res = requests.get(url, params=pld)
        json = res.json()
        items = json['results']
        cache[hash] = items
    return cache[hash]


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
                    link = param
                    if param == 'score':
                        link = 'relativeScore'
                    value = history[year][item['id']][link]
                except KeyError:
                    value = ''
                if key not in fieldnames:
                    fieldnames.append(key)
                item[key] = value


#TODO: refactoring
# It's already not needed for places and datasets,
# move it to Census for entries to remove from here?
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
