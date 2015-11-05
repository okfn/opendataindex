from .. import services
config = services.config.get_config()


# Interface

def run():
    print('Preparing datasets...')
    datasets = Datasets()
    datasets.run()
    print('Preparing entries...')
    entries = Entries()
    entries.run()
    print('Preparing questions...')
    questions = Questions()
    questions.run()
    print('Preparing places...')
    places = Places()
    places.run()
    print('Preparing summary...')
    summary = Summary()
    summary.run()


# Implement

class Datasets(object):

    # Public

    entity = 'datasets'
    fieldnames = [
        'id',
        'title',
        'category',
        'description',
        'icon',
        'rank',
        'score',
    ]

    def run(self):
        """Load, process and save items.
        """

        # Load history items by year
        history = services.data.load_history(self.entity)

        # Get current year items
        items = list(history[config.ODI['current_year']].values())

        # Update items
        for item in items:
            item['title'] = item['name']
            item['score'] = item['relativeScore']

        # Add prev years to items
        services.data.add_prev_years_to_items(history, self.fieldnames, items)

        # Sort and add rank to items
        services.data.sort_and_add_rank_to_items(items)

        # Save items as csv
        services.data.save_items(self.entity, self.fieldnames, items)


class Entries(object):

    # Public

    entity = 'entries'
    fieldnames = [
        'place',
        'dataset',
        'year',
        'rank',
        'score',
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
        """Load, process and save items.
        """

        # Get items
        items = []
        for year in config.ODI['years']:
            year_items = services.data.load_items(self.entity, year=year)
            for item in year_items:
                item[year] = year
            items.extend(year_items)

        # Update items
        for item in items:
            item['isopen'] = item['isOpen']
            item['submitters'] = item['submitter']
            item['reviewers'] = item['reviewer']

        # Add rank to items
        # e.g.: 1st place for 2014 year statistics dataset
        groups = {}
        for item in items:
            key = '-'.join([str(item['year']), item['dataset']])
            groups.setdefault(key, [])
            groups[key].append(item)
        items = []
        for key in sorted(groups, reverse=True):
            group_items = groups[key]
            services.data.sort_and_add_rank_to_items(group_items)
            items.extend(group_items)

        # Save items as csv
        services.data.save_items(self.entity, self.fieldnames, items)

    @classmethod
    def get_submitters_and_reviewers(cls):
        """Return submitters and reviwers indexed by place.
        """
        submitters = {}
        reviewers = {}
        history = services.data.load_history(cls.entity)
        for year in history:
            for item in history[year].values():
                place = item['place']
                submitters.setdefault(place, set())
                reviewers.setdefault(place, set())
                submitters[place].add(item['submitter'])
                reviewers[place].add(item['reviewer'])
        return {
            'submitters': submitters,
            'reviewers': reviewers,
        }

    @classmethod
    def get_statistics(cls):
        """Return statistics indexed by year.
        """
        stats = {}
        history = services.data.load_history(cls.entity)
        for year in history:
            datasets = set()
            places = set()
            isopen_count = 0
            entries = history[year]
            for item in history[year].values():
                datasets.add(item['dataset'])
                places.add(item['place'])
                if item['isOpen'] == 'Yes':
                    isopen_count += 1
            datasets_count = len(datasets)
            places_count = len(places)
            entries_count = len(entries)
            isopen_percent = int(100 * isopen_count / entries_count)
            stats[year] = {
                'datasets_count': datasets_count,
                'places_count': places_count,
                'entries_count': entries_count,
                'isopen_count': isopen_count,
                'isopen_percent': isopen_percent,
            }
        return stats


class Questions(object):

    # Public

    entity = 'questions'
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
        """Load, process and save items.
        """

        # Get items
        items = services.data.load_items(self.entity)

        # Update items
        for item in items:
            item['icon'] = config.ODI['icons'].get(item['icon'], '')

        # Save items as csv
        services.data.save_items(self.entity, self.fieldnames, items)


class Places(object):

    # Public

    entity = 'places'
    fieldnames = [
        'id',
        'name',
        'slug',
        'region',
        'continent',
        'submitters',
        'reviewers',
        'rank',
        'score',
    ]

    def run(self):
        """Load, process and save items.
        """

        # Load history items by year
        history = services.data.load_history(self.entity)

        # Get helper data
        sub_rev = Entries.get_submitters_and_reviewers()

        # Get current year items
        items = list(history[config.ODI['current_year']].values())

        # Update items
        for item in items:
            submitters = sub_rev['submitters'].get(item['id'], set())
            reviewers = sub_rev['reviewers'].get(item['id'], set())
            item['submitters'] = '~*'.join(submitters)
            item['reviewers'] = '~*'.join(reviewers)
            item['score'] = item['relativeScore']

        # Add prev years to items
        services.data.add_prev_years_to_items(history, self.fieldnames, items)

        # Sort and add rank to items
        services.data.sort_and_add_rank_to_items(items)

        # Save items as csv
        services.data.save_items(self.entity, self.fieldnames, items)


# TODO: refactoring
# Move stats logic to Census?
class Summary(object):

    # Public

    entity = 'summary'
    fieldnames = [
        'id',
        'title',
    ]
    metrics = [
        'places_count',
        'entries_count',
        'isopen_count',
        'isopen_percent',
    ]

    def run(self):
        """Load, process and save items.
        """

        # Get statistics
        stats = Entries.get_statistics()

        # Add value fieldnames
        fieldnames = list(self.fieldnames)
        for year in config.ODI['years']:
            key = self.generate_value_key(year)
            fieldnames.append(key)

        # Generate items
        items = []
        for metric in self.metrics:
            item = {'id': metric, 'title': metric}
            for year in config.ODI['years']:
                key = self.generate_value_key(year)
                item[key] = stats[year][metric]
            items.append(item)

        # Save items as csv
        services.data.save_items(self.entity, fieldnames, items)

    @classmethod
    def generate_value_key(cls, year):
        """Generate key like `value_2014` for year.
        """
        key = 'value'
        if year != config.ODI['current_year']:
            key = 'value_{year}'.format(year=year)
        return key
