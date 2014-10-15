import os
import json
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
        self.api_base = self.settings['DATASTORE']['api']['base']
        self.api_path = os.path.join(self.output_path, self.api_base)
        self.api_filters = self.settings['DATASTORE']['api']['filters']
        self.api_exclude = self.settings['DATASTORE']['api']['exclude']
        self.api_extension = '.json'

        if not os.path.exists(self.api_path):
            os.makedirs(self.api_path)

    def generate_output(self, writer):
        """Write the API files based on configuration."""

        for k, v in self.datasets.items():
            if not k in self.api_exclude:
                dest_name = '{0}{1}'.format(k, self.api_extension)
                dest_path = os.path.join(self.api_path, dest_name)

                with open(dest_path, 'w') as f:
                    f.write(v.json)

                # Now check if we need to generate filter endpoints
                if self.api_filters.get(k):
                    for filter_arg in self.api_filters[k]:
                        filters = frozenset(v[filter_arg])
                        # Generate an endpoint for each valid filter
                        for arg in filters:
                            arg_slug = arg.lower().replace(' ', '-')
                            fdest_dir = os.path.join(self.api_path, k)
                            if not os.path.exists(fdest_dir):
                                os.makedirs(fdest_dir)

                            fdest_name = '{0}{1}'.format(arg_slug,
                                                         self.api_extension)
                            fdest_path = os.path.join(fdest_dir, fdest_name)

                            # get the data that matches the filter
                            matches = [x for x in v.dict if x[filter_arg] == arg]

                            # write the filtered endpoint
                            with open(fdest_path, 'w') as f:
                                f.write(json.dumps(matches))


def get_generators(pelican_object):
    return APIGenerator


def register():
    signals.get_generators.connect(get_generators)
