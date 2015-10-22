from .. import services
config = services.config.get_config()


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

        # Get helper data
        max_score = Places.get_max_score()

        # Update history
        for year in history:
            for item in history[year].values():
                item['score'] = int(100 * item['score'] / max_score)

        # Get current year items
        items = list(history[config.ODI['current_year']].values())

        # Update items
        for item in items:
            item['title'] = item['name']

        # Add prev years to items
        services.data.add_prev_years(history, self.fieldnames, items)

        # Save items as csv
        services.data.save_items(self.entity, self.fieldnames, items)

    @classmethod
    def get_max_score(cls):
        """Return max available score.
        """
        questions_max_score = Questions.get_max_score()
        item_count = len(services.data.load_items(cls.entity))
        return questions_max_score * item_count


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
        items = services.data.load_items(self.entity)

        # Update items
        for item in items:
            item['isopen'] = item['isOpen']
            item['submitters'] = item['submitter']
            item['reviewers'] = item['reviewer']

        # Add rank to items
        datasets = {}
        for item in items:
            datasets.setdefault(item['dataset'], [])
            datasets[item['dataset']].append(item)
        for dataset_items in datasets.values():
            dataset_items.sort(key=lambda item: item['score'], reverse=True)
            current_rank = None
            current_score = None
            for num, item in enumerate(dataset_items):
                if current_score != item['score']:
                    current_rank = num + 1
                    current_score = item['score']
                item['rank'] = current_rank

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
            places = set()
            isopen_count = 0
            entries = history[year]
            for item in history[year].values():
                places.add(item['place'])
                if item['isOpen'] == 'Yes':
                    isopen_count += 1
            places_count = len(places)
            entries_count = len(entries)
            isopen_percent = int(100 * isopen_count / entries_count)
            stats[year] = {
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

        # Save items as csv
        services.data.save_items(self.entity, self.fieldnames, items)

    @classmethod
    def get_max_score(cls):
        """Return max available score.
        """
        score = 0
        items = services.data.load_items(cls.entity)
        for item in items:
            score += item['score']
        return score


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
        max_score = Datasets.get_max_score()
        sub_rev = Entries.get_submitters_and_reviewers()

        # Update history
        for year in history:
            for item in history[year].values():
                item['score'] = int(100 * item['score'] / max_score)

        # Get current year items
        items = list(history[config.ODI['current_year']].values())

        # Update items
        for item in items:
            submitters = sub_rev['submitters'].get(item['id'], set())
            reviewers = sub_rev['reviewers'].get(item['id'], set())
            item['submitters'] = '~*'.join(submitters)
            item['reviewers'] = '~*'.join(reviewers)

        # Add prev years to items
        services.data.add_prev_years(history, self.fieldnames, items)

        # Save items as csv
        services.data.save_items(self.entity, self.fieldnames, items)

    @classmethod
    def get_max_score(cls):
        """Return max available score.
        """
        questions_max_score = Questions.get_max_score()
        item_count = len(services.data.load_items(cls.entity))
        return questions_max_score * item_count


# TODO: refactor
class Summary(object):

    # Public

    entity = 'summary'
    fieldnames = [
        'id',
        'title',
        'value',
        'value_2014',
        'value_2013',
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

        # Generate items
        items = []
        for metric in self.metrics:
            item = {
                'id': metric,
                'title': metric,
                'value': stats['2015'][metric],
                'value_2014': stats['2014'][metric],
                'value_2013': stats['2013'][metric],
            }
            items.append(item)

        # Save items as csv
        services.data.save_items(self.entity, self.fieldnames, items)
