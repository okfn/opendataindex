import os
import sys
import codecs
import logging


class Populate(object):

    def __init__(self, *args, **kwargs):

        # TODO: tidy up the init method and import stuff from the right places

        SCRIPTS_ROOT = os.path.abspath(os.path.dirname(__file__))
        PROJECT_ROOT = os.path.abspath(os.path.dirname(SCRIPTS_ROOT))
        PLUGINS = os.path.join(PROJECT_ROOT, 'plugins')
        CONF = os.path.join(PROJECT_ROOT, 'pelicanconf.py')
        sys.path.insert(1, PLUGINS)
        sys.path.insert(1, CONF)

        import datastore

        self.conf = {
            'DATASTORE':
                {
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
            },
            'ODI': {
                'years': ['2014', '2013'],
                'current_year': '2014'
            }
        }

        ds = datastore.DataStore(self.conf)

        self.dest_path = os.path.join(PROJECT_ROOT, 'content', 'pages')
        self.file = 'index.md'
        self.empty_display_type = u'empty'
        self.na_display_type = u'na'
        self.datastore = ds.build()
        self.places = self.datastore['places'].dict
        self.datasets = self.datastore['datasets'].dict
        self.entries = self.datastore['entries'].dict
        self.years = self.conf['ODI']['years']
        self.current_year = self.conf['ODI']['current_year']

        # do it
        self.write_places()
        self.write_datasets()
        self.write_historical()

    def commit_file(self, filepath, filetemplate, filecontext):
        with open(filepath, 'w+') as f:
            f.write(filetemplate.format(**filecontext).encode('utf-8'))

    def ensure_dir(self, dirpath):
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

    def write_historical(self):
        """Write source files for historical overviews."""

        # set the default display_type
        display_type = 'overview'

        # ensure the historical directory exists
        historical_dir = os.path.join(self.dest_path, 'historical')
        self.ensure_dir(historical_dir)

        # write the historical overviews
        for year in self.years:
            if year != self.current_year:

                # ensure this historical/year directory exists
                dirpath = os.path.join(historical_dir, year)
                self.ensure_dir(dirpath)

                # write this historical/year index file
                filepath = os.path.join(dirpath, self.file)
                filecontext = {
                    'year': year,
                    'display_type': display_type
                }
                self.commit_file(filepath, historical_template, filecontext)

    def write_datasets(self):
        """Write source files for datasets."""

        # set the default display_type
        display_type = u'overview'

        # ensure the datasets directory exists
        datasets_dir = os.path.join(self.dest_path, 'datasets')
        self.ensure_dir(datasets_dir)

        # write the datasets overview
        filepath = os.path.join(datasets_dir, self.file)
        filecontext = {
            'year': self.current_year,
            'display_type': display_type
        }
        self.commit_file(filepath, dataset_overview_template, filecontext)

        # write files per dataset
        for dataset in self.datasets:

            # set the default display_type
            display_type = u'dataset'

            # ensure this dataset's directory exists
            dirpath = os.path.join(datasets_dir, dataset['id'])
            self.ensure_dir(dirpath)

            # write the dataset index file for the current year
            filepath = os.path.join(dirpath, self.file)
            filecontext = {
                'dataset_name': dataset['title'],
                'dataset_slug': dataset['id'],
                'year': self.current_year,
                'display_type': display_type
            }
            self.commit_file(filepath, dataset_template, filecontext)

            # write the dataset index file for other years
            for year in self.years:
                if year != self.current_year:

                    # ensure this dataset/year directory exists
                    dirpath = os.path.join(datasets_dir, dataset['id'], year)
                    self.ensure_dir(dirpath)

                    # write this dataset/year index file
                    filepath = os.path.join(dirpath, self.file)
                    filecontext = {
                        'dataset_name': dataset['title'],
                        'dataset_slug': dataset['id'],
                        'year': year,
                        'display_type': display_type
                    }
                    self.commit_file(filepath, dataset_historical_template,
                                     filecontext)

    def write_places(self):
        """Write source files for places."""

        # set the default display_type
        display_type = u'overview'

        # ensure the places directory exists
        places_dir = os.path.join(self.dest_path, 'places')
        self.ensure_dir(places_dir)

        # write the places overview
        filepath = os.path.join(places_dir, self.file)
        filecontext = {
            'year': self.current_year,
            'display_type': display_type
        }
        self.commit_file(filepath, place_overview_template, filecontext)

        # write files per place
        for place in self.places:

            # set the default display_type
            display_type = u'place'

            # ensure this place's directory exists
            dirpath = os.path.join(places_dir, place['id'])
            self.ensure_dir(dirpath)

            # write the place index file for the current year
            filepath = os.path.join(dirpath, self.file)
            filecontext = {
                'place_name': place['name'],
                'place_slug': place['id'],
                'year': self.current_year,
                'display_type': display_type
            }
            self.commit_file(filepath, place_template, filecontext)

            # write the place index file for other years
            for year in self.years:
                if year != self.current_year:

                    # the display type depends on the presence of entries
                    entries = [e for e in self.entries if
                               e['place'] == place['id'] and
                               e['year'] == year]

                    if not entries:
                        display_type = self.na_display_type

                    # ensure this place/year directory exists
                    dirpath = os.path.join(places_dir, place['id'], year)
                    self.ensure_dir(dirpath)

                    # write this place/year index file
                    filepath = os.path.join(dirpath, self.file)
                    filecontext = {
                        'place_name': place['name'],
                        'place_slug': place['id'],
                        'year': year,
                        'display_type': display_type
                    }
                    self.commit_file(filepath, place_historical_template,
                                     filecontext)

            # write place/dataset files
            for dataset in self.datasets:

                # set the default display_type
                display_type = u'place_dataset'

                # the display type depends on the presence of entries
                entries = [e for e in self.entries if
                           e['place'] == place['id'] and
                           e['dataset'] == dataset['id'] and
                           e['year'] == self.current_year]

                if not entries:
                    display_type = self.empty_display_type

                # ensure this place/dataset directory exists
                dirpath = os.path.join(places_dir, place['id'], 'datasets',
                                       dataset['id'])
                self.ensure_dir(dirpath)

                # write the place/dataset index file for the current year
                filepath = os.path.join(dirpath, self.file)
                filecontext = {
                    'place_name': place['name'],
                    'place_slug': place['id'],
                    'dataset_name': dataset['title'],
                    'dataset_id': dataset['id'],
                    'year': self.current_year,
                    'display_type': display_type
                }
                self.commit_file(filepath, place_dataset_template, filecontext)

                # write the place/dataset index file for other years
                for year in self.years:
                    if year != self.current_year:

                        # the display type depends on the presence of entries
                        entries = [e for e in self.entries if
                                   e['place'] == place['id'] and
                                   e['dataset'] == dataset['id'] and
                                   e['year'] == year]

                        if not entries:
                            display_type = self.na_display_type

                        # ensure this place/dataset/year directory exists
                        dirpath = os.path.join(dirpath, year)
                        self.ensure_dir(dirpath)

                        # write this place/dataset/year index file
                        filepath = os.path.join(dirpath, self.file)
                        filecontext = {
                            'place_name': place['name'],
                            'place_slug': place['id'],
                            'dataset_name': dataset['title'],
                            'dataset_id': dataset['id'],
                            'year': year,
                            'display_type': display_type
                        }
                        self.commit_file(filepath,
                                         place_dataset_historical_template,
                                         filecontext)


place_overview_template = u"""type: {display_type}
title: Places comparison
slug: places
year: {year}
"""


place_template = u"""type: {display_type}
title: {place_name}
slug: places/{place_slug}
place: {place_slug}
year: {year}
"""


place_historical_template = u"""type: {display_type}
title: {place_name}
slug: places/{place_slug}/{year}
place: {place_slug}
year: {year}
"""


place_dataset_template = u"""type: {display_type}
title: {place_name} / {dataset_name}
slug: places/{place_slug}/datasets/{dataset_id}
place: {place_slug}
dataset: {dataset_id}
year: {year}
"""


place_dataset_historical_template = u"""type: {display_type}
title: {place_name} / {dataset_name} ({year})
slug: places/{place_slug}/datasets/{dataset_id}/{year}
place: {place_slug}
dataset: {dataset_id}
year: {year}
"""


dataset_overview_template = u"""type: {display_type}
title: Dataset comparison
slug: datasets
year: {year}
"""


dataset_template = u"""type: {display_type}
title: {dataset_name}
slug: datasets/{dataset_slug}
dataset: {dataset_slug}
year: {year}
"""


dataset_historical_template = u"""type: {display_type}
title: {dataset_name}
slug: datasets/{dataset_slug}/{year}
dataset: {dataset_slug}
year: {year}
"""


historical_template = u"""type: {display_type}
title: Open Data Index {year}
slug: historical/{year}
year: {year}
"""


if __name__ == '__main__':
    Populate()
