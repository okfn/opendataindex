import os
import logging
import urllib
import shutil
import csv

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
    dictized = [ dict(zip(columns, row)) for row in rows ]
    return {
        'columns': columns,
        'rows': [columns] + rows,
        'dicts': dictized
        }

def _write_csv(rows, path):
    writer = csv.writer(open(path, 'w'), lineterminator='\n')
    writer.writerows(rows)

def extract():
    ## datasets
    out = _load_csv('tmp/datasets.csv')
    _write_csv(out['rows'], 'data/datasets.csv')

    ## questions
    out = _load_csv('tmp/questions.csv')
    # get rid of translations (column 8 onwards) for the time being as not
    # checked and not being used
    transposed = list(zip(*list(out['rows'])))
    newrows = list(zip(*(transposed[:8])))
    _write_csv(newrows, 'data/questions.csv')

    ## places
    places = _load_csv('tmp/places.csv')
    _write_csv(places['rows'], 'data/places.csv')


def cleanup():
    if os.path.exists('tmp'):
        shutil.rmtree('tmp')

def process():
    # download()
    extract()
    # cleanup()

if __name__ == '__main__':
    process()

