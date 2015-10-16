import os
from .. import services
config = services.config.get()


# Interface

def run():
    datasets = Datasets()
    datasets.run()
    entries = Entries()
    entries.run()
    questions = Questions()
    questions.run()
    places = Places()
    places.run()
    summary = Summary()
    summary.run()


# Implement

class Datasets(object):

    # Public

    source = config.ODI['database']['datasets']
    target = os.path.join(config.DATASTORE['location'], 'datasets.csv')
    fieldnames = [
        'id',
        'title',
        'category',
        'description',
        'icon',
        'score',
        'rank',
        'score_2014',
        'rank_2014',
    ]

    def run(self):
        items = services.data.load(self.source)
        services.data.save(items, fieldnames=self.fieldnames, path=self.target)


class Entries(object):

    # Public

    source = config.ODI['database']['entries']
    target = os.path.join(config.DATASTORE['location'], 'entries.csv')
    fieldnames = [
        'place',
        'dataset',
        'year',
        'score',
        'rank',
        'isopen',
        'dataset',
        'exists',
        'digital',
        'public',
        'online',
        'free',
        'machinereadable',
        'bulk',
        'openlicense',
        'uptodate',
        'url',
        'format',
        'licenseurl',
        'dateavailable',
        'officialtitle',
        'publisher',
        'timestamp',
        'submitters',
        'reviewers',
        'details',
    ]

    def run(self):
        items = services.data.load(self.source)
        services.data.save(items, fieldnames=self.fieldnames, path=self.target)


class Questions(object):

    # Public

    source = config.ODI['database']['questions']
    target = os.path.join(config.DATASTORE['location'], 'questions.csv')
    fieldnames = [
        'id',
        'question',
        'description',
        'type',
        'placeholder',
        'score',
        'icon',
        'dependants',
    ]

    def run(self):
        items = services.data.load(self.source)
        services.data.save(items, fieldnames=self.fieldnames, path=self.target)


class Places(object):

    # Public

    source = config.ODI['database']['places']
    target = os.path.join(config.DATASTORE['location'], 'places.csv')
    fieldnames = [
        'id',
        'name',
        'slug',
        'undefined',
        'region',
        'continent',
        'score',
        'rank',
        'score_2014',
        'rank_2014',
        'submitters',
        'reviewvers',
    ]

    def run(self):
        items = services.data.load(self.source)
        services.data.save(items, fieldnames=self.fieldnames, path=self.target)


class Summary(object):

    # Public

    source = config.ODI['database']['summary']
    target = os.path.join(config.DATASTORE['location'], 'summary.csv')
    fieldnames = [
        'id',
        'title',
        'value',
        'value_2014',
    ]

    def run(self):
        items = []
        services.data.save(items, fieldnames=self.fieldnames, path=self.target)
