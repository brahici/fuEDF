#!/usr/bin/python
#encoding: utf-8

import os
import unittest
import tempfile
import json
import bs4 as BeautifulSoup

import fuedf

_DB = None
_APP = None

DB_PATH = '/tmp/fuedf_test.db'

TABLES = [
    'fuedf_user',
    'fuedf_rate',
    'fuedf_consumption',
]

RATES_NAMES = [
    'BleuPleines', 'BleuCreuses',
    'BlancPleines', 'BlancCreuses',
    'RougePleines', 'RougeCreuses',
]

RATES_COLORS = [
    '#4572a7', '#4572a7',
    '#b6b6b6', '#b6b6b6',
    '#aa4643', '#aa4643'
]

DATA_SET_1 = [
    ['2012-01-01', 'BleuPleines', 200],
    ['2012-01-01', 'BleuCreuses', 400],
    ['2012-01-01', 'BlancPleines', 70],
    ['2012-01-01', 'BlancCreuses', 140],
    ['2012-01-01', 'RougePleines', 20],
    ['2012-01-01', 'RougeCreuses', 40],
]

DATA_SET_2 = [
    ['2012-01-08', 'BleuPleines', 300],
    ['2012-01-08', 'BleuCreuses', 600],
    ['2012-01-08', 'BlancPleines', 100],
    ['2012-01-08', 'BlancCreuses', 210],
    ['2012-01-08', 'RougePleines', 30],
    ['2012-01-08', 'RougeCreuses', 60],
]

DATA_SET_3 = [
    ['2012-01-15', 'BleuPleines', 350],
    ['2012-01-15', 'BleuCreuses', 690],
    ['2012-01-15', 'BlancPleines', 125],
    ['2012-01-15', 'BlancCreuses', 245],
    ['2012-01-15', 'RougePleines', 35],
    ['2012-01-15', 'RougeCreuses', 72],
]

def setUpModule():
    global _DB
    global _APP
    assert not os.path.exists(DB_PATH), 'setUpModule\nTest database found ! ' \
            'Remove it\n -> rm %s \n' \
            'then run again fuedf_tests.py\n' % DB_PATH
    fuedf.app.config['SQLALCHEMY_DATABASE_URI'] = \
            'sqlite:///' + DB_PATH
    _DB = fuedf.models.db
    fuedf.app.config['TESTING'] = True
    _APP = fuedf.app.test_client()
    fuedf.initdb()

def tearDownModule():
    if os.path.exists(DB_PATH):
        os.unlink(DB_PATH)


class FuedfTestCase(unittest.TestCase):

    def test_0000_initdb(self):
        tables = [tbl.name for tbl in _DB.get_tables_for_bind()]
        self.assertEqual(len(tables), 3)
        for table in TABLES:
            self.assertIn(table, tables)

    def test_0001_initdb_data(self):
        rates = fuedf.models.Rate.query.all()
        self.assertEqual(len(rates), 6)
        for rate in rates:
            self.assertIn(rate.name, RATES_NAMES)
        cons = fuedf.models.Consumption.query.all()
        self.assertEqual(len(cons), 0)
        users = fuedf.models.User.query.all()
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].name, 'Administrator')

    def test_0002_empty_db_main_page(self):
        res = _APP.get('/')
        self.assertIn('No entries so far', res.data)
        self.assertNotIn('Chart view', res.data)

    def test_0003_get_rates(self):
        rates_ref = {
            'BleuCreuses': 1,
            'BleuPleines': 2,
            'BlancCreuses': 3,
            'BlancPleines': 4,
            'RougeCreuses': 5,
            'RougePleines': 6,
        }
        rates = json.loads(_APP.get('/_get_rates').data)['rates']
        self.assertDictEqual(rates, rates_ref)

    def test_0004_insert_data_missing_data(self):
        msg_ref = 'A value is missing'
        res = _APP.post('/cons/add', data={'date': '', 'rate': 1, 'value': 5},
                follow_redirects=True)
        self.assertIn(msg_ref, res.data)
        res = _APP.post('/cons/add', data={'date': '2012-01-01', 'rate': '',
                'value': 5}, follow_redirects=True)
        self.assertIn(msg_ref, res.data)
        res = _APP.post('/cons/add', data={'date': '2012-01-01', 'rate': 1,
                'value': ''}, follow_redirects=True)
        self.assertIn(msg_ref, res.data)

    def test_0005_insert_data(self):
        rates = json.loads(_APP.get('/_get_rates').data)['rates']
        for data in DATA_SET_1:
            post_data = {
                    'date': data[0],
                    'rate': rates[data[1]],
                    'value': data[2]
            }
            _APP.post('/cons/add', data=post_data, follow_redirects=True)
        cons = fuedf.models.Consumption.query.all()
        self.assertEqual(len(cons), 6)
        res = _APP.get('/')
        for rate in RATES_NAMES:
            self.assertIn(rate, res.data)

    def test_0006_pagination_one_page(self):
        res = _APP.get('/')
        soup = BeautifulSoup.BeautifulSoup(res.data)
        dpn = soup.find(id='page_navigator')
        spans = dpn.find_all('span')
        self.assertEqual(len(spans), 4)
        for span in spans:
            self.assertIn('inactive', span.get('class'))
        self.assertEqual(soup.find(id='cons_total').text, '0')

    def test_0007_delta_check(self):
        fmC = fuedf.models.Consumption
        rates = json.loads(_APP.get('/_get_rates').data)['rates']
        for data in DATA_SET_2+DATA_SET_3:
            post_data = {
                    'date': data[0],
                    'rate': rates[data[1]],
                    'value': data[2]
            }
            _APP.post('/cons/add', data=post_data, follow_redirects=True)
        cons = fmC.query.filter(fmC.date==data[0]).all()
        self.assertEqual(len(cons), 6)
        offset = len(DATA_SET_2)+len(DATA_SET_3)+1
        for row in cons:
            self.assertEqual(row.delta,
                    DATA_SET_3[row.rid-offset][2] - \
                            DATA_SET_2[row.rid-offset][2])

    def test_0008_pagination_three_pages_first(self):
        res = _APP.get('/')
        soup = BeautifulSoup.BeautifulSoup(res.data)
        dpn = soup.find(id='page_navigator')
        spans = dpn.find_all('span')
        self.assertEqual(len(spans), 2)
        anchors = dpn.find_all('a')
        for span in spans:
            self.assertIn('inactive', span.get('class'))
        self.assertEqual('/?page=2', anchors[0].get('href'))
        self.assertEqual('/?page=3', anchors[1].get('href'))
        total = sum([e[0]-e[1] for e in zip([data[2] for data in DATA_SET_3],
                [data[2] for data in DATA_SET_2])])
        self.assertEqual(soup.find(id='cons_total').text, str(total))

    def test_0009_pagination_three_pages_second(self):
        res = _APP.get('/?page=2')
        soup = BeautifulSoup.BeautifulSoup(res.data)
        dpn = soup.find(id='page_navigator')
        spans = dpn.find_all('span')
        self.assertEqual(len(spans), 0)
        anchors = dpn.find_all('a')
        for anchor in anchors[0:2]:
            self.assertEqual('/?page=1', anchor.get('href'))
        for anchor in anchors[2:]:
            self.assertEqual('/?page=3', anchor.get('href'))
        total = sum([e[0]-e[1] for e in zip([data[2] for data in DATA_SET_2],
                [data[2] for data in DATA_SET_1])])
        self.assertEqual(soup.find(id='cons_total').text, str(total))

    def test_0010_pagination_three_pages_third(self):
        res = _APP.get('/?page=3')
        soup = BeautifulSoup.BeautifulSoup(res.data)
        dpn = soup.find(id='page_navigator')
        spans = dpn.find_all('span')
        self.assertEqual(len(spans), 2)
        anchors = dpn.find_all('a')
        for span in spans:
            self.assertIn('inactive', span.get('class'))
        self.assertEqual('/?page=1', anchors[0].get('href'))
        self.assertEqual('/?page=2', anchors[1].get('href'))
        self.assertEqual(soup.find(id='cons_total').text, '0')

    def test_0011_chart_view(self):
        res = _APP.get('/charts')
        soup = BeautifulSoup.BeautifulSoup(res.data)
        self.assertEqual(soup.find(id='chart_container').text, '')
        date_start = soup.find(id='date_start')
        for option in date_start.find_all('option'):
            if option.get('selected') == 'selected':
                self.assertEqual(option.get('value'), DATA_SET_1[0][0])
        date_end = soup.find(id='date_end')
        for option in date_end.find_all('option'):
            if option.get('selected') == 'selected':
                self.assertEqual(option.get('value'), DATA_SET_3[0][0])

    def test_0012_get_charts_data_dates_rates_colors(self):
        res = json.loads(_APP.get('/_get_charts_data?mode=values').data)
        self.assertListEqual(res['colors'], RATES_COLORS)
        self.assertListEqual(res['rates'], RATES_NAMES)
        self.assertListEqual(res['dates'],
                [DATA_SET_1[0][0], DATA_SET_2[0][0], DATA_SET_3[0][0]])

    def test_0013_get_charts_data_values(self):
        res = json.loads(_APP.get('/_get_charts_data?mode=values').data) \
                ['values']
        ref = [list(l) for l in zip(
                [0 for i in range(6)] ,
                [e[0]-e[1] for e in zip([data[2] for data in DATA_SET_2],
                        [data[2] for data in DATA_SET_1])],
                [e[0]-e[1] for e in zip([data[2] for data in DATA_SET_3],
                        [data[2] for data in DATA_SET_2])]
                )
        ]
        vals = res.values()
        # need to sort values else test does not succeed
        # no matter, test values were chosen in order to be unique
        vals.sort()
        ref.sort()
        self.assertListEqual(vals, ref)

    def test_0014_get_charts_data_progressive(self):
        res = json.loads(_APP.get('/_get_charts_data?mode=progressive').data) \
                ['values']
        ref = [list(l) for l in zip(
                [0 for i in range(6)],
                [e[0]-e[1] for e in zip(
                        [data[2] for data in DATA_SET_2],
                        [data[2] for data in DATA_SET_1])],
                [e[0]-e[1] for e in zip(
                        [data[2] for data in DATA_SET_3],
                        [data[2] for data in DATA_SET_1])],
        )]
        vals = res.values()
        # need to sort values else test does not succeed
        # no matter, test values were chosen in order to be unique
        vals.sort()
        ref.sort()
        self.assertListEqual(vals, ref)

    def test_0015_get_charts_data_total(self):
        res = json.loads(_APP.get('/_get_charts_data?mode=total').data) \
                ['values']
        ref = [list(e) for e in zip([data[2] for data in DATA_SET_1],
                [data[2] for data in DATA_SET_2],
                [data[2] for data in DATA_SET_3])
        ]
        vals = res.values()
        # need to sort values else test does not succeed
        # no matter, test values were chosen in order to be unique
        vals.sort()
        ref.sort()
        self.assertListEqual(vals, ref)

    def test_0016_get_charts_data_global(self):
        res = json.loads(_APP.get('/_get_charts_data?mode=global').data) \
                ['values']
        ref = [
            sum([0 for i in range(6)]),
            sum([e[0]-e[1] for e in zip([data[2] for data in DATA_SET_2],
                    [data[2] for data in DATA_SET_1])]),
            sum([e[0]-e[1] for e in zip([data[2] for data in DATA_SET_3],
                [data[2] for data in DATA_SET_2])])
        ]
        vals = res['Global']
        # need to sort values else test does not succeed
        # no matter, test values were chosen in order to be unique
        vals.sort()
        ref.sort()
        self.assertListEqual(vals, ref)

if __name__ == '__main__':
    unittest.main(verbosity=2)

