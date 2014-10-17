import os
import shutil
import json
from pelican import generators
from pelican import signals
import datastore


class AssetGenerator(generators.Generator):

    """Generates downloadable assets from a Pelican Datastore."""

    def __init__(self, *args, **kwargs):
        super(AssetGenerator, self).__init__(*args, **kwargs)

        self.datastore_path = self.settings['DATASTORE']['location']
        self.dest_path = os.path.join(self.settings['OUTPUT_PATH'],
                                      self.settings['THEME_STATIC_DIR'],
                                      self.settings['DATASTORE']['assets']['location'])
        self.archive_format = 'gztar'
        self.timestamp = self.settings['TIMESTAMP']
        # self.assets_exclude = self.settings['DATASTORE']['assets']['exclude']

    def write_archive(self):
        """Write an archive of the data as a public asset."""

        name = '{0}{1}'.format('opendataindex_data_', self.timestamp)
        archive_name = os.path.join(self.dest_path, name)
        shutil.make_archive(archive_name, self.archive_format,
                            self.datastore_path)

    def generate_output(self, writer):
        """Write the assets based on configuration."""

        self.write_archive()
        # TODO: Other public asset generators

def get_generators(pelican_object):
    return AssetGenerator


def register():
    signals.get_generators.connect(get_generators)
