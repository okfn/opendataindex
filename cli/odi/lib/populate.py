import os
import sys
import codecs
import shutil
import logging


def run(limited_places=None, limited_datasets=None):
    Populate(limited_places=limited_places, limited_datasets=limited_datasets)


class Populate(object):

    def __init__(self, *args, **kwargs):

        base_path = os.path.join(os.getcwd())
        PROJECT_ROOT = base_path
        PLUGINS = os.path.join(PROJECT_ROOT, 'plugins')
        CONF = os.path.join(PROJECT_ROOT,)
        sys.path.append(PLUGINS)
        sys.path.append(CONF)

        import datastore
        import config_default
        self.conf = {
            'DATASTORE': config_default.DATASTORE,
            'ODI': config_default.ODI
        }

        ds = datastore.DataStore(self.conf)

        self.dest_path = os.path.join(PROJECT_ROOT, 'content', 'pages')
        self.datasets_dir = os.path.join(self.dest_path, 'datasets')
        self.places_dir = os.path.join(self.dest_path, 'places')
        self.file = 'index.md'
        self.empty_display_type = u'empty'
        self.na_display_type = u'na'
        self.datastore = ds.build()
        self.places = self.datastore['places'].dict
        self.datasets = self.datastore['datasets'].dict
        self.entries = self.datastore['entries'].dict
        self.years = self.conf['ODI']['years']
        self.current_year = self.conf['ODI']['current_year']

        if kwargs.get('limited_places'):
            self.places = [p for p in self.places if
                           p['id'] in kwargs['limited_places']]

        if kwargs.get('limited_datasets'):
            self.datasets = [d for d in self.datasets if
                           d['id'] in kwargs['limited_datasets']]

        self.ensure_dir(self.datasets_dir, clean_slate=True)
        self.ensure_dir(self.places_dir, clean_slate=True)

        self.write_places()
        self.write_datasets()

    def commit_file(self, filepath, filetemplate, filecontext):
        with open(filepath, 'w+') as f:
            f.write(filetemplate.format(**filecontext).encode('utf-8'))

    def ensure_dir(self, dirpath, clean_slate=False):
        if clean_slate and os.path.exists(dirpath):
            shutil.rmtree(dirpath)
        if not os.path.exists(dirpath):
            os.makedirs(dirpath)

    def write_datasets(self):
        """Write source files for datasets."""

        # set the default display_type
        display_type = u'datasets'

        # write the datasets overview
        filepath = os.path.join(self.datasets_dir, self.file)
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
            dirpath = os.path.join(self.datasets_dir, dataset['id'])
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
                    dirpath = os.path.join(self.datasets_dir, dataset['id'],
                                           year)
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
        display_type = u'places'

        # write the places overview
        filepath = os.path.join(self.places_dir, self.file)
        filecontext = {
            'year': self.current_year,
            'display_type': display_type
        }
        self.commit_file(filepath, overview_template, filecontext)

        # write the historical overviews
        for year in self.years:
            if year != self.current_year:

                # ensure this places/year directory exists
                dirpath = os.path.join(self.places_dir, year)
                self.ensure_dir(dirpath)

                # write this places/year index file
                filepath = os.path.join(dirpath, self.file)
                filecontext = {
                    'year': year,
                    'display_type': display_type
                }
                self.commit_file(filepath, overview_historical_template, filecontext)

        # write files per place
        for place in self.places:

            # set the default display_type
            display_type = u'place'

            # the display type depends on the presence
            # of entries in the current year
            entries = [e for e in self.entries if
                       e['place'] == place['id'] and
                       e['year'] == self.current_year]

            if not entries:
                display_type = self.empty_display_type

            # ensure this place's directory exists
            dirpath = os.path.join(self.places_dir, place['id'])
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
                    dirpath = os.path.join(self.places_dir, place['id'], year)
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
                dirpath = os.path.join(self.places_dir, place['id'],
                                       'datasets', dataset['id'])
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


overview_template = u"""type: {display_type}
template: {display_type}
title: Open Data Index
slug: places
year: {year}
"""


overview_historical_template = u"""type: {display_type}
template: {display_type}
title: Open Data Index {year}
slug: places/{year}
year: {year}
"""

place_template = u"""type: {display_type}
template: {display_type}
title: {place_name}
slug: places/{place_slug}
place: {place_slug}
year: {year}
"""


place_historical_template = u"""type: {display_type}
template: {display_type}
title: {place_name}
slug: places/{place_slug}/{year}
place: {place_slug}
year: {year}
"""


place_dataset_template = u"""type: {display_type}
template: {display_type}
title: {place_name} / {dataset_name}
slug: places/{place_slug}/datasets/{dataset_id}
place: {place_slug}
dataset: {dataset_id}
year: {year}
"""


place_dataset_historical_template = u"""type: {display_type}
template: {display_type}
title: {place_name} / {dataset_name} ({year})
slug: places/{place_slug}/datasets/{dataset_id}/{year}
place: {place_slug}
dataset: {dataset_id}
year: {year}
"""


dataset_overview_template = u"""type: {display_type}
template: {display_type}
title: Dataset comparison
slug: datasets
year: {year}
"""


dataset_template = u"""type: {display_type}
template: {display_type}
title: {dataset_name}
slug: datasets/{dataset_slug}
dataset: {dataset_slug}
year: {year}
"""


dataset_historical_template = u"""type: {display_type}
template: {display_type}
title: {dataset_name}
slug: datasets/{dataset_slug}/{year}
dataset: {dataset_slug}
year: {year}
"""
