import os
import tablib
from pelican import signals


class DataStore(object):

    """Interface for static file datastore.

    self.build() returns a dict where `key` is the name of the dataset,
    and `value` is a tablib.Dataset object.

    At present, should support any file format that tablib can import:
    * csv
    * json
    * yaml
    * see tablib for full support.

    """

    def __init__(self, config, **kwargs):
        self.config = config
        self.intrafield_delimiter = self.config['DATASTORE']['intrafield_delimiter']
        # TODO: handle the required settings
        if not 'DATASTORE' in self.config:
            raise KeyError

    def process(self):
        """Converts source files in the datastore into Python objects.

        Returns a list of pairs, like (key, dataset)

        """

        datasets = []

        for source in self.get_sources():
            _path, ext = os.path.splitext(source)

            if ext in self.config['DATASTORE']['formats']:
                _head, key = os.path.split(_path)
                dataset_raw = self._extract_data(source)
                if dataset_raw:
                    dataset_clean = self._clean_data(dataset_raw)
                    datasets.append((key, dataset_clean))

        return datasets

    def build(self):
        """Return processed datasets as a dict to add to meta context."""

        rv = {}

        for dataset in self.process():
            rv[dataset[0]] = dataset[1]
        return rv

    def get_location(self):
        return self.config['DATASTORE']['location']

    def get_sources(self):

        # TODO: check for file types
        # TODO: have a configurable list of file types or names
        # to add to sources
        # TODO: support namespacing based on folder nesting: eg:
        # datastore.govt.spending
        # if source was: data/govt/spending.csv

        sources = []

        for (dirpath, _, filenames) in os.walk(self.get_location()):
            sources.extend(os.path.join(dirpath, filename) for
                           filename in filenames)

        return sources

    def _extract_data(self, data_source):
        """Create a Dataset object from the data source."""

        with open(data_source) as f:
            stream = f.read()
            extracted = tablib.import_set(stream)

        # TODO: Notify which sources could not be serialized by tablib
        return extracted

    def _clean_data(self, raw_dataset):
        """Takes the raw Dataset and cleans it up."""

        dataset_clean_headers = self._normalize_headers(raw_dataset)
        dataset_clean = self._normalize_rows(dataset_clean_headers)

        return dataset_clean

    def _normalize_headers(self, dataset):
        """Clean up the headers of each Dataset."""

        transform_chars = {
            # Note: We allow the "_" symbol in headers.
            ord('-'): None,
            ord('"'): None,
            ord(' '): None,
            ord("'"): None,
        }

        for index, header in enumerate(dataset.headers):
            tmp = unicode(header).translate(transform_chars).lower()
            dataset.headers[index] = tmp

        return dataset

    def _normalize_rows(self, dataset):
        """Clean up each object in the Dataset."""

        workspace = dataset.dict

        for item in workspace:
            for k, v in item.iteritems():

                # remove whitespace
                item[k] = v.strip()

                if v in self.config['DATASTORE']['true_strings']:
                    item[k] = True

                if v in self.config['DATASTORE']['false_strings']:
                    item[k] = False

                if v in self.config['DATASTORE']['none_strings']:
                    item[k] = None

                if self.intrafield_delimiter in v:
                    item[k] = v.split(self.intrafield_delimiter)

        dataset.dict = workspace

        return dataset


def data(page_generator_init):
    datastore = DataStore(page_generator_init.settings)
    page_generator_init.context['datastore'] = datastore.build()


def register():
    signals.page_generator_init.connect(data)
