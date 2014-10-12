import os
import logging
import urllib
import shutil
import csv
from collections import OrderedDict

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdGNBWWJDaTlnMU1wN1BQZlgxNHBxd0E&usp=drive_web#gid=0
survey_submissions = 'https://docs.google.com/spreadsheet/pub?key=0AqR8dXc6Ji4JdGNBWWJDaTlnMU1wN1BQZlgxNHBxd0E&single=true&gid=0&output=csv'
survey_entries = 'https://docs.google.com/spreadsheet/pub?key=0AqR8dXc6Ji4JdGNBWWJDaTlnMU1wN1BQZlgxNHBxd0E&single=true&gid=1&output=csv'

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdFI0QkpGUEZyS0wxYWtLdG1nTk9zU3c&usp=drive_web#gid=0
survey_questions = 'https://docs.google.com/spreadsheet/pub?key=0AqR8dXc6Ji4JdFI0QkpGUEZyS0wxYWtLdG1nTk9zU3c&single=true&gid=0&output=csv'

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0Aon3JiuouxLUdEVHQ0c4RGlRWm9Gak54NGV0UlpfOGc&usp=drive_web#gid=0
survey_datasets = 'https://docs.google.com/spreadsheet/pub?key=0Aon3JiuouxLUdEVHQ0c4RGlRWm9Gak54NGV0UlpfOGc&single=true&gid=0&output=csv'

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdE1QUS1qNjhvRDJaQy1TbTdJZDMtNFE&usp=drive_web#gid=1
survey_places = 'https://docs.google.com/spreadsheet/pub?key=0AqR8dXc6Ji4JdE1QUS1qNjhvRDJaQy1TbTdJZDMtNFE&single=true&gid=1&output=csv'

# download source data from the survey to tmp directory
def download():
    if not os.path.exists('tmp'):
        os.makedirs('tmp')
    urllib.urlretrieve(survey_submissions, 'tmp/submissions.csv')
    urllib.urlretrieve(survey_entries, 'tmp/entries.csv')
    urllib.urlretrieve(survey_questions, 'tmp/questions.csv')
    urllib.urlretrieve(survey_datasets, 'tmp/datasets.csv')
    urllib.urlretrieve(survey_places, 'tmp/places.csv')

def _load_csv(path):
    reader = csv.reader(open(path))
    columns = reader.next()
    # lowercase the columnss
    columns = [ x.lower() for x in columns ]
    rows = [ row for row in reader ]
    dictized = [ AttrDict(dict(zip(columns, row))) for row in rows ]
    return AttrDict({
        'columns': columns,
        'rows': [columns] + rows,
        'dicts': dictized
        })

def _write_csv(rows, path):
    writer = csv.writer(open(path, 'w'), lineterminator='\n')
    writer.writerows(rows)

class AttrDict(dict): 
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

def extract():
    # At the moment we will only have an entry for current year and will not
    # record earlier years. Sometimes we may not have new data for current year
    # (previous year is still good) and we will then use that previous year
    # entry as this year's entry
    # TODO: support multiple years

    places = _load_csv('tmp/places.csv')
    entries = _load_csv('tmp/entries.csv')
    datasets = _load_csv('tmp/datasets.csv')
    questions = _load_csv('tmp/questions.csv')

    current_year = '2014'
    # this will be entry dicts keyed by a tuple of (place_id, dataset_id)
    keyed_entries = OrderedDict()

    ## entries

    # algorithm
    # 1. create dict keyed by place, dataset (year?)
    # 2. Walk through current rows and add in

    for p in places['dicts']:
        for d in datasets['dicts']:
            keyed_entries[(p['id'], d['id'])] = AttrDict({
                    'place': p['id'],
                    'dataset': d['id'],
                    'year': current_year,
                    'timestamp': ''
                    })
            
    # walk through existing entries and use the latest year entry we have for a
    # given place + dataset
    for ent in entries['dicts']:
        # delete censusid column
        del ent['censusid']
        key = (ent['place'], ent['dataset'])
        if (keyed_entries[key].timestamp == '' # no existing entry (just stubbed one)
            or ent['year'] > keyed_entries[key].year # existing entry is newer
            ):
            keyed_entries[key] = ent

    ## write the entries.csv

    # play around with column ordering in entries.csv
    # drop off censusid (first col) and timestamp
    fieldnames = entries.columns[2:]
    # move year around
    fieldnames[0:3] = ['place', 'dataset', 'year']
    # move timestamp to the end
    fieldnames.insert(-1, 'timestamp')

    writer = csv.DictWriter(open('data/entries.csv', 'w'),
            fieldnames=fieldnames,
            lineterminator='\n'
            )
    writer.writeheader()
    writer.writerows(keyed_entries.values())

    ## datasets
    _write_csv(datasets['rows'], 'data/datasets.csv')

    ## questions
    # get rid of translations (column 8 onwards) for the time being as not
    # checked and not being used
    transposed = list(zip(*list(questions['rows'])))
    newrows = list(zip(*(transposed[:8])))
    _write_csv(newrows, 'data/questions.csv')

    ## places
    _write_csv(places['rows'], 'data/places.csv')


def cleanup():
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')

def process():
    download()
    extract()
    # cleanup()

if __name__ == '__main__':
    process()

