import os
import logging
import urllib
import shutil
import csv
import operator
import unittest
from collections import OrderedDict
from pprint import pprint

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdGNBWWJDaTlnMU1wN1BQZlgxNHBxd0E&usp=drive_web#gid=0
survey_submissions = 'https://docs.google.com/spreadsheet/pub?key=0AqR8dXc6Ji4JdGNBWWJDaTlnMU1wN1BQZlgxNHBxd0E&single=true&gid=0&output=csv'
survey_entries = 'https://docs.google.com/spreadsheet/pub?key=0AqR8dXc6Ji4JdGNBWWJDaTlnMU1wN1BQZlgxNHBxd0E&single=true&gid=1&output=csv'

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdFI0QkpGUEZyS0wxYWtLdG1nTk9zU3c&usp=drive_web#gid=0
survey_questions = 'https://docs.google.com/spreadsheet/pub?key=0AqR8dXc6Ji4JdFI0QkpGUEZyS0wxYWtLdG1nTk9zU3c&single=true&gid=0&output=csv'

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0Aon3JiuouxLUdEVHQ0c4RGlRWm9Gak54NGV0UlpfOGc&usp=drive_web#gid=0
survey_datasets = 'https://docs.google.com/spreadsheet/pub?key=0Aon3JiuouxLUdEVHQ0c4RGlRWm9Gak54NGV0UlpfOGc&single=true&gid=0&output=csv'

# https://docs.google.com/a/okfn.org/spreadsheet/ccc?key=0AqR8dXc6Ji4JdE1QUS1qNjhvRDJaQy1TbTdJZDMtNFE&usp=drive_web#gid=1
survey_places = 'https://docs.google.com/spreadsheet/pub?key=0AqR8dXc6Ji4JdE1QUS1qNjhvRDJaQy1TbTdJZDMtNFE&single=true&gid=1&output=csv'

class AttrDict(dict): 
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__

class Processor(object):
    def download(self):
        '''Download source data from the survey to tmp directory.'''
        if not os.path.exists('tmp'):
            os.makedirs('tmp')
        urllib.urlretrieve(survey_submissions, 'tmp/submissions.csv')
        urllib.urlretrieve(survey_entries, 'tmp/entries.csv')
        urllib.urlretrieve(survey_questions, 'tmp/questions.csv')
        urllib.urlretrieve(survey_datasets, 'tmp/datasets.csv')
        urllib.urlretrieve(survey_places, 'tmp/places.csv')

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
        # this will be entry dicts keyed by a tuple of (place_id, dataset_id)
        self.keyed_entries = OrderedDict()

        # stub out the keyed entries
        for p in self.places['dicts']:
            for d in self.datasets['dicts']:
                self.keyed_entries[(p['id'], d['id'])] = AttrDict({
                        'place': p['id'],
                        'dataset': d['id'],
                        'year': self.current_year,
                        'timestamp': ''
                        })

    def run(self):
        self.run_entries()
        self.run_datasets()
        self.run_questions()
        self.run_places()

    def run_entries(self):
        keyed_entries = self.keyed_entries
        ## entries

        # walk through existing entries and use the latest year entry we have for a
        # given place + dataset
        for ent in self.entries.dicts:
            self._tidy_entry(ent)
            key = (ent['place'], ent['dataset'])
            if (keyed_entries[key].timestamp == '' # no existing entry (just stubbed one)
                or ent['year'] > keyed_entries[key].year # existing entry is newer
                ):
                keyed_entries[key] = ent

        self._rank_entries()

        ## write the entries.csv

        # play around with column ordering in entries.csv
        # drop off censusid (first col) and timestamp
        fieldnames = self.entries.columns[2:]
        # move year around
        fieldnames[0:3] = ['place', 'dataset', 'year']
        fieldnames.insert(3, 'score')
        fieldnames.insert(4, 'rank')
        # move timestamp to the end
        fieldnames.insert(-1, 'timestamp')

        writer = csv.DictWriter(open('data/entries.csv', 'w'),
                fieldnames=fieldnames,
                lineterminator='\n'
                )
        writer.writeheader()
        writer.writerows(keyed_entries.values())

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

        ## score then rank
        # 10 datasets * 100 score per dataset
        total_possible_score = 10 * 100.0
        for place in self.places.dicts:
            score = sum([x.score for x in self.entries.dicts if x.place == place.id])
            # score is a percentage (runs from 0 to 100)
            # TODO: should we round like this as we lose distinction b/w 68 an
            # 68.5
            score = int(round(100 * score / total_possible_score, 0))
            place['score'] = score

        byscore = sorted(self.places.dicts, key=operator.itemgetter('score'),
                reverse=True)
        rank = 1
        last_score = 10000 # a large number bigger than max score
        for count, place in enumerate(byscore):
            if place.score < last_score:
                rank = count + 1
            last_score = place.score
            place['rank'] = rank

        self._write_csv(self.places.dicts, 'data/places.csv', fieldnames)

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

    def _score(self, entry):
        def summer(memo, qu):
            if qu.score and entry[qu.id] == 'Y':
                memo = memo + int(qu.score)
            return memo;
        return reduce(summer, self.questions.dicts, 0)

    def _rank_entries(self):
        def _tmp(_dict):
            return (_dict['dataset'], -_dict['score'])
        tmpsort = sorted(self.entries.dicts, key=_tmp)
        # now walk through and assign ranks
        # ranks are per dataset (i.e. we rank places per dataset)
        # equal scores get same rank
        current_rank, count, last_score = [1,0,0]
        def reset():
            current_rank = 1
            count = 0
            last_score = 0
        last_dataset = 'budget'
        for entry in tmpsort:
            count += 1
            # reset on each new dataset
            if entry.dataset != last_dataset:
                reset()
            if entry.score < last_score:
                current_rank = count

            last_dataset = entry.dataset
            last_score = entry.score
            entry['rank'] = current_rank

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

    def test_place_scores(self):
        out = dict([[x.id, x] for x in self.places.dicts])
        self.assertEqual(out['gb'].score, '94')
        self.assertEqual(out['au'].score, '66')

    def test_place_rank(self):
        out = dict([[x.id, x] for x in self.places.dicts])
        self.assertEqual(out['gb'].rank, '1')
        self.assertEqual(out['au'].rank, '10')

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

