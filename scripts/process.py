import os
import sys
import logging
import urllib
import shutil
import csv
import operator
import unittest
from collections import OrderedDict
from pprint import pprint


def get_config():
    base_path = os.path.join(os.getcwd())
    sys.path.append(base_path)
    import config_default
    config = config_default.ODI['cli']
    sys.path.remove(base_path)
    return config


config = get_config()

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdGNBWWJDaTlnMU1wN1BQZlgxNHBxd0E&usp=drive_web#gid=0
survey_submissions = config['database']['submissions']
survey_entries = config['database']['entries']

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdFI0QkpGUEZyS0wxYWtLdG1nTk9zU3c&usp=drive_web#gid=0
survey_questions = config['database']['questions']

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0Aon3JiuouxLUdEVHQ0c4RGlRWm9Gak54NGV0UlpfOGc&usp=drive_web#gid=0
survey_datasets = config['database']['datasets']

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdE1QUS1qNjhvRDJaQy1TbTdJZDMtNFE&usp=drive_web#gid=1
survey_places = config['database']['places']


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

# At the moment we will only have an entry for current year and will not
# record earlier years. Sometimes we may not have new data for current year
# (previous year is still good) and we will then use that previous year
# entry as this year's entry
# TODO: support multiple years
class Extractor(object):
    def __init__(self):
        self.places = self._load_csv('tmp/places.csv')
        self.entries = self._load_csv('tmp/entries.csv')
        self.datasets = self._load_csv('tmp/datasets.csv')
        self.questions = self._load_csv('tmp/questions.csv')

        self.current_year = '2014'
        self.years = ['2014', '2013']

        # this will be entry dicts keyed by a tuple of (place_id, dataset_id)
        self.keyed_entries = OrderedDict()

        # after the processing and copying, this has every entry to be written
        self.writable_entries = OrderedDict()

        # stub out the keyed entries
        for p in self.places['dicts']:
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
        for ent in self.entries.dicts:
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

        writer = csv.DictWriter(open('data/entries.csv', 'w'),
                fieldnames=fieldnames,
                lineterminator='\n'
                )
        writer.writeheader()
        writer.writerows([x[1] for x in self.writable_entries.iteritems()])

    def run_datasets(self):
        self._write_csv(self.datasets['rows'], 'data/datasets.csv')

    def run_questions(self):
        # get rid of translations (column 8 onwards) for the time being as not
        # checked and not being used
        transposed = list(zip(*list(self.questions.rows)))
        newrows = list(zip(*(transposed[:8])))
        self._write_csv(newrows, 'data/questions.csv')

    def run_places(self):
        fieldnames = self.places.columns
        fieldnames += ['score', 'rank']
        extra_years = [y for y in self.years if y != self.current_year]
        for year in extra_years:
            fieldnames += ['score_{0}'.format(year), 'rank_{0}'.format(year)]

        ## score then rank
        for place in self.places.dicts:
            # write score and rank for each year we have
            for year in self.years:
                total_places = len(set([x[1].place for x in self.writable_entries.iteritems() if x[1].year == year]))
                score_lookup = 'score'
                rank_lookup = 'rank'
                if not year == self.current_year:
                    score_lookup = 'score_{0}'.format(year)
                    rank_lookup = 'rank_{0}'.format(year)

                to_score = [x[1].score for x in
                            self.writable_entries.iteritems() if
                            x[1].place == place.id and x[1].year == year and
                            x[1].score is not None]

                if not to_score:
                    score = None
                    rank = total_places
                else:
                    score = sum(to_score)
                    # TODO: rank
                    rank = total_places

                # 10 datasets * 100 score per dataset
                total_possible_score = 10 * 100.0

                # score is a percentage (runs from 0 to 100)
                # TODO: should we round like this as we lose distinction b/w 68 an
                # 68.5

                # if place.id == 'au':
                #     import ipdb;ipdb.set_trace()

                if not score is None:
                    score = int(round(100 * score / total_possible_score, 0))

                place[score_lookup] = score
                place[rank_lookup] = rank

            # byscore = sorted(self.places.dicts,
            #                  key=operator.itemgetter(score_lookup),
            #                  reverse=True)
            # # now rank
            # # for year in self.years:
            # rank = 1
            # last_score = 10000 # a large number bigger than max score
            # for count, place in enumerate(byscore):
            #     if place[score_lookup] < last_score:
            #         rank = count + 1
            #     last_score = place[score_lookup]
            #     place[rank_lookup] = rank

        self._write_csv(self.places.dicts, 'data/places.csv', fieldnames)

    def run_summary(self):
        fieldnames = ['id', 'title', 'value']
        extra_years = [y for y in self.years if y != self.current_year]
        for year in extra_years:
            fieldnames += ['value_{0}'.format(year)]

        rows = [
            ['places_count', 'Number of Places'],
            ['entries_count', 'Number of Entries'],
            ['open_count', 'Number of Open Datasets'],
            ['open_percent', 'Percent Open']
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
            year_numopen = len([x for x in self.entries.dicts if x.isopen])
            year_percentopen = int(round((100.0 * year_numopen) /
                                          year_numentries, 0))
            rows[0].append(year_numplaces)
            rows[1].append(year_numentries)
            rows[2].append(year_numopen)
            rows[3].append(year_percentopen)

        self._write_csv([fieldnames] + rows, 'data/summary.csv')

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

        rv = OrderedDict()

        def _tmp(_dict):
            return _dict[1]['dataset'], -_dict[1]['score']

        for year in self.years:
            year_entries = OrderedDict(
                sorted([e for e in entries.iteritems() if
                        e[0][2] == year], key=_tmp)
            )

            # assign rank for entries in scope of place/dataset/year
            current_rank, count, last_score = [1,0,0]
            def reset():
                current_rank = 1
                count = 0
                last_score = 0
            last_dataset = 'budget'
            for k, v in year_entries.iteritems():
                count += 1
                # reset on each new dataset
                if v.dataset != last_dataset:
                    reset()
                if v.score < last_score:
                    current_rank = count

                last_dataset = v.dataset
                last_score = v.score
                v.rank = current_rank

            rv.update(year_entries)

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
        self.entries = Extractor._load_csv('data/entries.csv')
        self.places = Extractor._load_csv('data/places.csv')
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
        summary_all = Extractor._load_csv('data/summary.csv')
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

