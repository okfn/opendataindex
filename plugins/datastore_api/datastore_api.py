import os
import json
import tablib
from pelican import generators
from pelican import signals
import datastore


class APIGenerator(generators.Generator):

    """Generates an API from a Pelican Datastore.

    Supports filtered endpoints.

    """

    def __init__(self, *args, **kwargs):
        super(APIGenerator, self).__init__(*args, **kwargs)
        self.backend = datastore.DataStore(self.settings)
        self.datasets = self.backend.build()
        self.output_path = self.settings['OUTPUT_PATH']
        self.api_base = self.settings['DATASTORE']['api']['base']
        self.api_path = os.path.join(self.output_path, self.api_base)
        self.api_filters = self.settings['DATASTORE']['api']['filters']
        self.api_exclude = self.settings['DATASTORE']['api']['exclude']
        self.api_formats = self.settings['DATASTORE']['api']['formats']

        if not os.path.exists(self.api_path):
            os.makedirs(self.api_path)

    def generate_output(self, writer):
        """Write the API files based on the current configuration."""

        for k, v in self.datasets.items():
            # write the full dataset endpoints
            self.write_set(k, v)

            # write the slice endpoints, if any are defined
            if self.api_filters.get(k):
                for y in self.api_filters.get(k):
                    self.write_slice(k, v, y)

    def write_set(self, name, dataset):
        """Write an API endpoint for each complete dataset."""

        if not name in self.api_exclude:
            for api_format in self.api_formats:
                dest_name = '{0}{1}{2}'.format(name, '.', api_format)
                dest_path = os.path.join(self.api_path, dest_name)

                if not os.path.exists(self.api_path):
                    os.makedirs(self.api_path)

                with open(dest_path, 'w+') as f:
                    f.write(getattr(dataset, api_format))

    def write_slice(self, name, dataset, slice_attr):
        """Write an API endpoint for this dataset slice."""

        if not name in self.api_exclude:
            # Get the unique values in the dataset for `slice_attr`
            slice_values = frozenset(dataset[slice_attr])

            # Write a slice for each unique value
            for _slice in slice_values:
                sliced_dataset = self.get_sliced_dataset(dataset, slice_attr,
                                                          _slice)
                slice_slug = _slice.lower().replace(' ', '-').replace(',', '-')
                slice_dir = os.path.join(self.api_path, name)

                if not os.path.exists(slice_dir):
                    os.makedirs(slice_dir)

                for api_format in self.api_formats:
                    dest_name = '{0}{1}{2}'.format(slice_slug, '.', api_format)
                    dest_path = os.path.join(slice_dir, dest_name)
                    with open(dest_path, 'w+') as f:
                        f.write(getattr(sliced_dataset, api_format))

    def get_sliced_dataset(self, dataset, slice_attr, slice_value):
        """Return a new tablib.Dataset based on passed data."""

        sliced_dataset = tablib.Dataset()
        sliced_dataset.dict = [obj for obj in dataset.dict if
                               obj[slice_attr] == slice_value]
        return sliced_dataset


def get_generators(pelican_object):
    return APIGenerator


def register():
    signals.get_generators.connect(get_generators)
