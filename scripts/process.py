import os
import sys
import logging
import urllib
import shutil
import csv
import operator
import itertools
import unittest
from collections import OrderedDict
from pprint import pprint


def get_config():
    base_path = os.path.join(os.getcwd())
    sys.path.append(base_path)
    import config_default
    config = config_default.ODI
    sys.path.remove(base_path)
    return config


def get_datastore_config():
    base_path = os.path.join(os.getcwd())
    sys.path.append(base_path)
    import config_default
    config = config_default.DATASTORE
    sys.path.remove(base_path)
    return config

config = get_config()
datastore_config = get_datastore_config()

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdGNBWWJDaTlnMU1wN1BQZlgxNHBxd0E&usp=drive_web#gid=0
survey_submissions = config['database']['submissions']
survey_entries = config['database']['entries']

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdFI0QkpGUEZyS0wxYWtLdG1nTk9zU3c&usp=drive_web#gid=0
survey_questions = config['database']['questions']

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0Aon3JiuouxLUdEVHQ0c4RGlRWm9Gak54NGV0UlpfOGc&usp=drive_web#gid=0
survey_datasets = config['database']['datasets']

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdE1QUS1qNjhvRDJaQy1TbTdJZDMtNFE&usp=drive_web#gid=1
survey_places = config['database']['places']

entries_dest = os.path.join(datastore_config['location'], 'entries.csv')
submissions_dest = os.path.join(datastore_config['location'], 'submissions.csv')
questions_dest = os.path.join(datastore_config['location'], 'questions.csv')
datasets_dest = os.path.join(datastore_config['location'], 'datasets.csv')
places_dest = os.path.join(datastore_config['location'], 'places.csv')
summary_dest = os.path.join(datastore_config['location'], 'summary.csv')


class AttrDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


class Processor(object):
    def download(self):
        '''Download source data from the survey to tmp directory.'''
        if not os.path.exists(config['tmp_path']):
            os.makedirs(config['tmp_path'])
        urllib.urlretrieve(survey_submissions, '{0}/submissions.csv'.format(config['tmp_path']))
        urllib.urlretrieve(survey_entries, '{0}/entries.csv'.format(config['tmp_path']))
        urllib.urlretrieve(survey_questions, '{0}/questions.csv'.format(config['tmp_path']))
        urllib.urlretrieve(survey_datasets, '{0}/datasets.csv'.format(config['tmp_path']))
        urllib.urlretrieve(survey_places, '{0}/places.csv'.format(config['tmp_path']))

    def extract(self):
        '''Extract data from raw Survey files, process and save to data dir'''
        ext = Extractor()
        ext.run()

    def cleanup(self):
        if os.path.exists('tmp'):
            shutil.rmtree('tmp')

    def run(self):
        '''Run all stages of the processing pipeline'''
        self.download()
        self.extract()
        # keep tmp around so we can run extract without download
        # self.cleanup()

    def test(self):
        '''Run tests against extracted data to check all is good.'''
        suite = unittest.TestLoader().loadTestsFromTestCase(TestIndexData)
        unittest.TextTestRunner(verbosity=2).run(suite)


class Extractor(object):
    def __init__(self):
        self.places = self._load_csv('tmp/places.csv')
        self.entries = self._load_csv('tmp/entries.csv')
        self.datasets = self._load_csv('tmp/datasets.csv')
        self.questions = self._load_csv('tmp/questions.csv')
        self.submissions = self._load_csv('tmp/submissions.csv')

        self.current_year = '2014'
        self.years = ['2014', '2013']
        self.like_base_year = '2013' # the baseline for "like" comparisons
        self.remove_places = ['tc', 'ae', 'ua', 'kn', 'vg', 'ye', 'bh', 'bs',
                              'lc', 'bb', 'va', 'bt', 'gi', 'ky', 'gg', 'je',
                              'ly', 'jo']
        self.remove_2013_only = ['om', 'pk', 'ma']

        # this will be entry dicts keyed by a tuple of (place_id, dataset_id)
        self.keyed_entries = OrderedDict()

        # after the processing and copying, this has every entry to be written
        self.writable_entries = OrderedDict()

        # stub out the keyed entries
        for p in [p for p in self.places['dicts'] if
                  not p['id'] in self.remove_places]:
            for d in self.datasets['dicts']:
                for year in self.years:
                    self.keyed_entries[(p['id'], d['id'], year)] = AttrDict({
                            'place': p['id'],
                            'dataset': d['id'],
                            'year': year,
                            'timestamp': '',
                            'score': None,
                            'rank': None
                    })

    def run(self):
        # `self.run_entries()` must *always* run first!
        self.run_entries()
        self.run_datasets()
        self.run_questions()
        self.run_places()
        self.run_summary()

    def run_entries(self):

        # walk through the existing entries;
        # copy *forward* any missing place,dataset,year entries
        # eg:
        #   gb,timetables,2013 (have entry)
        #   gb,timetables,2014 (no entry: so copy the 2013 entry forward to 2014)
        for ent in [e for e in self.entries.dicts if
                    not e['place'] in self.remove_places]:
            self._tidy_entry(ent)
            key = (ent['place'], ent['dataset'], ent['year'])
            self.keyed_entries[key] = ent

        entries_to_write = {}
        populated_entries = {k: v for k, v in self.keyed_entries.items() if
                             v['timestamp'] != ''}
        entries_to_write.update(populated_entries)
        empty_entries = {k: v for k, v in self.keyed_entries.items() if
                         v['timestamp'] == ''}

        # if we have empty entries (should do),
        # then we need to do the copy forward
        if empty_entries:
            for k, v in empty_entries.items():
                related_entries = {x: y for x, y in
                                   populated_entries.iteritems() if
                                   v['place'] == y.place and
                                   v['dataset'] == y.dataset}

                if not related_entries:
                    pass
                else:

                    candidates = [int(key[2]) for key in
                                  related_entries.keys() if
                                  int(key[2]) < int(k[2])]
                    if candidates:
                        # if candidates is empty, then it means we only
                        # had related entries forward in time, so we *don't*
                        # have any copy forward to do
                        year_to_copy = max(candidates)
                        entry_to_copy = AttrDict(related_entries[(k[0], k[1], str(year_to_copy))].copy())
                        entry_to_copy['year'] = k[2]
                        entries_to_write.update({
                            k: entry_to_copy
                        })

        for k, v in entries_to_write.iteritems():
            # contribution is cumulative, so we just include all
            rel_submissions = [s for s in self.submissions.dicts if
                               s['place'] == v['place'] and
                               s['dataset'] == v['dataset']]

            v['submitters'] = '~*'.join(set([s['submitter'] for s in rel_submissions if s['submitter']]))
            v['reviewers'] = '~*'.join(set([s['reviewer'] for s in rel_submissions if s['reviewer']]))

        # remove 2013s marked for filtering
        entries_to_write = {k: v for k, v in entries_to_write.iteritems()
                            if not (k[0] in self.remove_2013_only
                            and k[2] == '2013')}

        self.writable_entries = AttrDict(self._rank_entries(OrderedDict(entries_to_write)))

        ## write the entries.csv

        # play around with column ordering in entries.csv
        # drop off censusid (first col) and timestamp
        fieldnames = self.entries.columns[1:]
        # move year around
        fieldnames[0:3] = ['place', 'dataset', 'year']
        fieldnames.insert(3, 'score')
        fieldnames.insert(4, 'rank')
        fieldnames.insert(5, 'isopen')
        # move timestamp to the end
        fieldnames.insert(-1, 'timestamp')
        fieldnames.insert(-1, 'submitters')
        fieldnames.insert(-1, 'reviewers')

        writer = csv.DictWriter(open(entries_dest, 'w'),
                fieldnames=fieldnames,
                lineterminator='\n'
                )
        writer.writeheader()
        writer.writerows([x[1] for x in self.writable_entries.iteritems()])

    def run_datasets(self):
        fieldnames = self.datasets.columns
        fieldnames += ['score', 'rank']
        extra_years = [y for y in self.years if y != self.current_year]
        for year in extra_years:
            fieldnames += ['score_{0}'.format(year), 'rank_{0}'.format(year)]

        ## set scores
        for dataset in self.datasets.dicts:
            for year in self.years:
                score_lookup = 'score'
                if not year == self.current_year:
                    score_lookup = 'score_{0}'.format(year)

                to_score = [x[1].score for x in
                            self.writable_entries.iteritems() if
                            x[1].dataset == dataset.id and x[1].year == year and
                            x[1].score is not None]

                # place count * 100 score per place
                place_count = len(set([x[0][0] for x in
                            self.writable_entries.iteritems() if
                            x[1].dataset == dataset.id and
                            x[1].year == year and
                            x[1].score is not None]))

                total_possible_score = place_count * 100.0

                if not to_score:
                    score = None
                else:
                    score = int(round(100 * sum(to_score) /
                                total_possible_score, 0))

                dataset[score_lookup] = score

        # build lookups for rank, now that we have scores
        lookup = {}
        for year in self.years:
            score_lookup = 'score'
            rank_lookup = 'rank'
            if not year == self.current_year:
                score_lookup = 'score_{0}'.format(year)
                rank_lookup = 'rank_{0}'.format(year)
            year_scores = sorted(list(set([d[score_lookup] for d in
                                 self.datasets.dicts])))
            year_scores.reverse()
            year_lookup = {}
            for index, score in enumerate(year_scores):
                if score is None:
                    pass
                else:
                    year_lookup.update({str(score): index + 1})

            lookup.update({year: year_lookup})

        # set ranks
        for dataset in self.datasets.dicts:
            for year in self.years:
                score_lookup = 'score'
                rank_lookup = 'rank'
                if not year == self.current_year:
                    score_lookup = 'score_{0}'.format(year)
                    rank_lookup = 'rank_{0}'.format(year)

                if dataset[score_lookup] is None:
                    dataset[rank_lookup] = None
                else:
                    dataset[rank_lookup] = lookup[year][str(dataset[score_lookup])]

        self._write_csv(self.datasets.dicts, datasets_dest, fieldnames)

    def run_questions(self):
        # get rid of translations (column 8 onwards) for the time being as not
        # checked and not being used
        icon_translate = {
            'file-alt': 'file-o',
            'eye-open': 'eye',
            'keyboard': 'keyboard-o',
            'time': 'clock-o'
        }
        transposed = list(zip(*list(self.questions.rows)))
        newrows = list(zip(*(transposed[:8])))
        for index, q in enumerate(newrows):
            if q[6] and q[6] in icon_translate:
                q = list(q)
                q[6] = icon_translate[q[6]]
                q = tuple(q)
                newrows[index] = q

        self._write_csv(newrows, questions_dest)

    def run_places(self):
        fieldnames = self.places.columns
        fieldnames += ['score', 'rank']
        extra_years = [y for y in self.years if y != self.current_year]
        for year in extra_years:
            fieldnames += ['score_{0}'.format(year), 'rank_{0}'.format(year)]
        fieldnames += ['submitters', 'reviewers']

        cleaned_places = [p for p in self.places.dicts if
                          not p['id'] in self.remove_places]

        ## set scores
        for place in cleaned_places:
            for year in self.years:
                score_lookup = 'score'
                if not year == self.current_year:
                    score_lookup = 'score_{0}'.format(year)

                to_score = [x[1].score for x in
                            self.writable_entries.iteritems() if
                            x[1].place == place.id and x[1].year == year and
                            x[1].score is not None]

                # 10 datasets * 100 score per dataset
                total_possible_score = 10 * 100.0

                if not to_score:
                    score = None
                else:
                    score = int(round(100 * sum(to_score) /
                                total_possible_score, 0))

                place[score_lookup] = score

        # build lookups for rank, now that we have scores
        lookup = {}
        for year in self.years:
            score_lookup = 'score'
            rank_lookup = 'rank'
            if not year == self.current_year:
                score_lookup = 'score_{0}'.format(year)
                rank_lookup = 'rank_{0}'.format(year)
            year_scores = sorted(list(set([p[score_lookup] for p in
                                 cleaned_places])), reverse=True)
            year_lookup = {}
            year_lookup.update({
                str(max(year_scores)): {
                    'rank': 1,
                    'score': max(year_scores),
                    'keys': []
                }
            })
            for place in cleaned_places:

                if place[score_lookup] is None:
                    pass
                else:
                    if str(place[score_lookup]) in year_lookup.keys():
                        year_lookup[str(place[score_lookup])]['keys'].append(place['id'])
                    else:
                        year_lookup.update({
                            str(place[score_lookup]): {
                                'rank': None,
                                'score': place[score_lookup],
                                'keys': [place['id']]
                            }
                        })
            sort_by_score = sorted(year_lookup.values(), key=operator.itemgetter('score'), reverse=True)
            lookup.update({year: sort_by_score})

        # set ranks per year
        for place in cleaned_places:
            for year in self.years:
                score_lookup = 'score'
                rank_lookup = 'rank'
                if not year == self.current_year:
                    score_lookup = 'score_{0}'.format(year)
                    rank_lookup = 'rank_{0}'.format(year)

                rank = 1
                for value in lookup[year]:
                    qty = len(value['keys'])
                    if place['id'] in value['keys']:
                        place[rank_lookup] = rank
                    rank += qty

        # set reviewers and submitters
        submitreviewlookup = {}
        for submission in [s for s in self.submissions.dicts if
                           not s['place'] in self.remove_places]:
            if submitreviewlookup.get(submission['place']):
                submitreviewlookup[submission['place']]['submitters'].append(submission['submitter'])
                submitreviewlookup[submission['place']]['reviewers'].append(submission['reviewer'])
            else:
                submitreviewlookup.update({
                    submission['place']: {
                        'reviewers': [submission['reviewer']],
                        'submitters': [submission['submitter']]
                    }
                })

        for place in cleaned_places:
            if place['id'] in submitreviewlookup:
                place['submitters'] = '~*'.join(set([s for s in submitreviewlookup[place['id']]['submitters'] if s]))
                place['reviewers'] = '~*'.join(set([r for r in submitreviewlookup[place['id']]['reviewers'] if r]))

        self._write_csv(cleaned_places, places_dest, fieldnames)

    def run_summary(self):
        fieldnames = ['id', 'title', 'value']
        extra_years = [y for y in self.years if y != self.current_year]
        for year in extra_years:
            fieldnames += ['value_{0}'.format(year)]

        rows = [
            ['places_count', 'Number of Places'],
            ['entries_count', 'Number of Entries'],
            ['open_count', 'Number of Open Datasets'],
            ['open_percent', 'Percent Open'],
            ['open_percent_like_for_like', 'Percent Open (like for like)']
        ]

        for year in self.years:
            value_lookup = 'value'
            if not year == self.current_year:
                value_lookup = 'value_{0}'.format(year)
            year_numentries = len([x for x in self.writable_entries if
                                   x[2] == year])
            year_numplaces = len(set([x[0] for x in
                                      self.writable_entries if
                                      x[2] == year]))
            year_numopen = len([x for x, z in self.writable_entries.iteritems() if z.isopen and x[2] == year])
            year_percentopen = int(round((100.0 * year_numopen) /
                                          year_numentries, 0))

            # like for like % open
            if year == self.like_base_year:
                year_percentopen_like_for_like = year_percentopen
            else:
                base_year_places = set([x[0] for x in
                                       self.writable_entries if
                                       x[2] == self.like_base_year])
                like_numentries = len([x for x in self.writable_entries
                                    if x[0] in base_year_places
                                    and x[2] == year])
                like_numopen = len([x for x, z in
                                    self.writable_entries.iteritems() if
                                    z.isopen and x[0] in base_year_places
                                    and x[2] == year])
                year_percentopen_like_for_like = int(
                    round((100.0 * like_numopen) / like_numentries, 0))

            rows[0].append(year_numplaces)
            rows[1].append(year_numentries)
            rows[2].append(year_numopen)
            rows[3].append(year_percentopen)
            rows[4].append(year_percentopen_like_for_like)

        self._write_csv([fieldnames] + rows, summary_dest)

    def _tidy_entry(self, entry_dict):
        # TODO: tidy up timestamp
        del entry_dict['censusid']

        # standardize y/n values (should go into DB at some point!)
        correcter = {
            'yes': 'Y',
            'yes ': 'Y',
            'no': 'N',
            'no ': 'N',
            'unsure': '?'
        }

        format_translations = {
            'xml': 'XML',
            '.xml': 'XML',
            'csv': 'CSV',
            '.csv': 'CSV',
            'tsv': 'TSV',
            '.tsv': 'TSV',
            'excel': 'EXCEL',
            'xls': 'EXCEL',
            'xlsx': 'EXCEL',
            '.xls': 'EXCEL',
            '.xlsx': 'EXCEL',
            'html': 'HTML',
            '.html': 'HTML',
            'pdf': 'PDF',
            '.pdf': 'PDF',
        }

        for k, v in format_translations.items():
            if k in entry_dict['format'].upper():
                entry_dict['format'] = entry_dict['format'].upper().replace(k, v)

        for qu in self.questions.dicts:
            # y/n questions have a weight
            if qu.score and int(qu.score) > 0:
                entry_dict[qu.id] = correcter[entry_dict[qu.id].lower()]

        entry_dict['rank'] = ''
        entry_dict['score'] = self._score(entry_dict)
        # Data is exists, is open, and publicly available, machine readable etc
        entry_dict['isopen'] = bool(
            entry_dict.exists == 'Y' and
            entry_dict.openlicense == 'Y' and
            entry_dict.public == 'Y' and
            entry_dict.bulk == 'Y' and
            entry_dict.machinereadable == 'Y'
          )

    def _score(self, entry):
        def summer(memo, qu):
            if qu.score and entry[qu.id] == 'Y':
                memo = memo + int(qu.score)
            return memo;
        return reduce(summer, self.questions.dicts, 0)

    def _rank_entries(self, entries):

        def _datasetscoresort(obj):
            return obj[1]['dataset'], -obj[1]['score']

        def _scoresort(obj):
            return obj[1]['score']

        rv = OrderedDict()
        workspace = []

        for year in self.years:
            year_entries = OrderedDict(sorted([e for e in entries.iteritems() if e[0][2] == year], key=_datasetscoresort))

            for dataset in [d[0] for d in self.datasets['rows'][1:]]:
                workspace.append(OrderedDict(sorted([(k, v) for k, v in
                                year_entries.iteritems() if k[1] == dataset],
                                key=_scoresort, reverse=True)))

        for o in workspace:
            scores = sorted(list(set([v['score'] for k, v in o.iteritems()])), reverse=True)
            score_map = {}
            score_map.update({
                str(max(scores)): {
                    'rank': 1,
                    'score': max(scores),
                    'keys': []
                }
            })

            for e in o.iteritems():
                if str(e[1]['score']) in score_map.keys():
                    score_map[str(e[1]['score'])]['keys'].append(e[0])
                else:
                    score_map.update({
                        str(e[1]['score']): {
                            'rank': None,
                            'score': e[1]['score'],
                            'keys': [e[0]]
                        }
                    })
            sort_by_score = sorted(score_map.values(), key=operator.itemgetter('score'), reverse=True)
            rank = 1
            for index, value in enumerate(sort_by_score):
                for key in value['keys']:
                    qty = len(value['keys'])
                    o[key]['rank'] = rank
                rank += qty

            rv.update(OrderedDict(o))
        return rv

    @classmethod
    def _load_csv(self, path):
        reader = csv.reader(open(path))
        columns = reader.next()
        # lowercase the columnss
        columns = [ x.lower() for x in columns ]
        rows = [ row for row in reader ]
        dictized = [ AttrDict(dict(zip(columns, row))) for row in rows ]
        return AttrDict({
            'columns': columns,
            'rows': [columns] + rows,
            'dicts': dictized
            })

    def _write_csv(self, rows, path, fieldnames=None):
        if fieldnames:
            writer = csv.DictWriter(open(path, 'w'), fieldnames=fieldnames, lineterminator='\n')
            writer.writeheader()
        else:
            writer = csv.writer(open(path, 'w'), lineterminator='\n')
        writer.writerows(rows)


class TestIndexData(unittest.TestCase):
    def setUp(self):
        self.entries = Extractor._load_csv(entries_dest)
        self.places = Extractor._load_csv(places_dest)
        self.keyed = dict([ [(e.place, e.dataset), e] for e in
            self.entries.dicts ])

    def test_entries_score(self):
        au_timetables = self.keyed[('au', 'timetables')]
        au_elections = self.keyed[('au', 'elections')]
        self.assertEqual(au_timetables.score, '45')
        self.assertEqual(au_elections.score, '100')

    def test_entries_rank(self):
        out = self.keyed[('ca', 'budget')]
        self.assertEqual(out.rank, '1')

    def test_entries_isopen(self):
        out = self.keyed[('gb', 'spending')]
        self.assertEqual(out.isopen, 'True')

    def test_place_scores(self):
        out = dict([[x.id, x] for x in self.places.dicts])
        self.assertEqual(out['gb'].score, '94')
        self.assertEqual(out['au'].score, '66')

    def test_place_rank(self):
        out = dict([[x.id, x] for x in self.places.dicts])
        self.assertEqual(out['gb'].rank, '1')
        self.assertEqual(out['au'].rank, '10')

    def test_summary(self):
        summary_all = Extractor._load_csv(summary_dest)
        summary = AttrDict([[x.id, x] for x in summary_all.dicts])

        self.assertEqual(summary.places_count.value, '249')
        self.assertEqual(summary.open_count.value, '86')
        self.assertEqual(summary.open_percent.value, '11')

import sys
import optparse
import inspect

def _object_methods(obj):
    methods = inspect.getmembers(obj, inspect.ismethod)
    methods = filter(lambda (name,y): not name.startswith('_'), methods)
    methods = dict(methods)
    return methods

if __name__ == '__main__':
    _methods = _object_methods(Processor)

    usage = '''%prog {action}

Actions:
    '''
    usage += '\n    '.join(
        [ '%s: %s' % (name, m.__doc__.split('\n')[0] if m.__doc__ else '') for (name,m)
        in sorted(_methods.items()) ])
    parser = optparse.OptionParser(usage)
    # Optional: for a config file
    # parser.add_option('-c', '--config', dest='config',
    #         help='Config file to use.')
    options, args = parser.parse_args()

    if not args or not args[0] in _methods:
        parser.print_help()
        sys.exit(1)

    method = args[0]
    getattr(Processor(), method)(*args[1:])

