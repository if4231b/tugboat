
import sys
import os
PROJECT_HOME = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(PROJECT_HOME)

import unittest
from requests import Request
import urllib
from unittest import TestCase
from datetime import datetime
from werkzeug.datastructures import MultiDict

from tugboat.views import ClassicSearchRedirectView

class TestSearchParametersTranslation(TestCase):
    """
    Test translation of each of the classic search parameters

    """

    def append_defaults(self):
        return MultiDict([('aut_syn', 'YES'), ('ttl_syn', 'YES'), ('txt_syn', 'YES'),
                          ('aut_wt',  '1.0'), ('obj_wt',  '1.0'), ('ttl_wt',  '0.3'), ('txt_wt',  '3.0'),
                          ('aut_wgt', 'YES'), ('obj_wgt', 'YES'), ('ttl_wgt', 'YES'), ('txt_wgt', 'YES'),
                          ('ttl_sco', 'YES'), ('txt_sco', 'YES'),
                          ('sim_query', 'YES'), ('ned_query', 'YES'),
                          ('min_score', ''),
                          ('data_type', 'SHORT'),
                          ('start_entry_day', ''), ('start_entry_mon', ''), ('start_entry_year', ''),
                          ('end_entry_day', ''), ('end_entry_mon', ''), ('end_entry_year', '')])

    def test_authors(self):
        """authors: single, multple, quoted,  and/or"""

        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        empty_search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&format=SHORT' + '/', empty_search, 'author test')  # no authors

        req.args = MultiDict([('author', urllib.quote('+Huchra, John'))])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        # parentheses are not urlencoded
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&format=SHORT' + '/',
                         author_search) # single author no quotes

        req.args = MultiDict([('author', urllib.quote('Huchra\r\n-Huchra,John'))])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra" AND -"Huchra,John"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&format=SHORT' + '/',
                         author_search) # single author with quotes

        req.args = MultiDict([('author', urllib.quote('Huchra, John\r\nMacri, Lucas M.'))])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" AND "Macri, Lucas M."') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&format=SHORT' + '/',
                         author_search) # authors, newline separator

        req.args = MultiDict([('author', urllib.quote('+Huchra, John;-Macri, Lucas M.'))])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" AND -"Macri, Lucas M."') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&format=SHORT' + '/',
                         author_search) # authors, semicolon separator

        req.args = MultiDict([('author', urllib.quote('Huchra, John')), ('aut_xct', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('=author:') + '(' + urllib.quote('"Huchra, John"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&format=SHORT' + '/',
                         author_search) # author with exact match

        # changing OR to AND and issuing a warning
        # 10/30/2019 From Alberto: let's recognize what boolean user has used
        req.args = MultiDict([('author', urllib.quote('Huchra, John;Macri, Lucas M.')), ('aut_logic', 'OR')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" OR "Macri, Lucas M."') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') +
                         '&format=SHORT' + '/',
                         author_search) # authors with or

    def test_object(self):
        """object: single, multple, etc"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.args = MultiDict()
        req.mimetype = None
        req.args = MultiDict([('object', urllib.quote('M31'))])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('"M31"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search) # single object

        req.args = MultiDict([('object', urllib.quote('M31\r\nM32'))])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('"M31" AND "M32"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/',
                         search) # objects, newline separator

        req.args = MultiDict([('object', urllib.quote('M31;M32;M33'))])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('"M31" AND "M32" AND "M33"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/',
                         search) # object, semicolor separator

    def test_title(self):
        """title field"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('title', urllib.quote('ADS'))])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('title:') + '(' + urllib.quote('ADS') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search) # single object

        req.args = MultiDict([('title', urllib.quote('ADS Kurtz')), ('ttl_logic', 'OR')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('title:') + '(' + urllib.quote('ADS Kurtz') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search) # single object

    def test_text(self):
        """text search"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('text', urllib.quote('M31'))])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('abs:') + '(' + urllib.quote('M31') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search) # single object

        req.args = MultiDict([('text', urllib.quote('foo bar')), ('txt_logic', 'OR')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('abs:') + '(' + urllib.quote('foo bar') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search) # single object

    def test_pubdate(self):
        """test pubdate"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.args = MultiDict()
        req.args.update(self.append_defaults())
        req.mimetype = None
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)  # no pub date

        req.args = MultiDict([('start_year', 1990), ('end_year', 1991)])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-01 TO 1991-12]') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)  # both years only

        req.args = MultiDict([('start_year', 1990), ('start_mon', 5), ('end_year', 1991), ('end_mon', 10)])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO 1991-10]') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)  # years and months

        req.args = MultiDict([('start_year', 1990), ('end_year', 1991), ('end_mon', 10)])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-01 TO 1991-10]') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search) # no start mon

        req.args = MultiDict([('start_year', 1990), ('start_mon', 5), ('end_year', 1991)])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO 1991-12]') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search) # no end mon

        req.args = MultiDict([('start_year', 1990), ('start_mon', 5)])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        n = datetime.now()
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO *]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search) # no end

        req.args = MultiDict([('end_year', 1991), ('end_mon', 10)])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[* TO 1991-10]') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search) # no start


    def test_database(self):
        """database can be astronomy or physics

        not clear how to test with more than one database set"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('db_key', 'AST')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        # the search query should be 'q=*:*&fq={!type=aqp v=$fq_database}&fq_database=(database:"astronomy")'
        # but with only some of the special characters html encoded
        self.assertEqual('filter_database_fq_database=OR' +
                         '&filter_database_fq_database=database:"astronomy"' +
                         '&q=*:*&fq=%7B!type%3Daqp%20v%3D%24fq_database%7D&fq_database=(database%3A%22astronomy%22)' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/',
                         search)  # astronomy only

        req.args = MultiDict([('db_key', 'PHY')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('filter_database_fq_database=OR' +
                         '&filter_database_fq_database=database:"physics"' +
                         '&q=*:*&fq=%7B!type%3Daqp%20v%3D%24fq_database%7D&fq_database=(database%3A%22physics%22)' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/',
                         search) # physics only

        req.args = MultiDict([('db_key', 'GEN')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +
                         '&error_message=' + 'UNRECOGNIZABLE_VALUE' + '&unprocessed_parameter=' + 'db_key' + '/', search) # general only

    def test_article_sel(self):
        """article_sel to property:article"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('article_sel', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('filter_doctype_facet_hier_fq_doctype=AND' +
                         '&filter_doctype_facet_hier_fq_doctype=' + urllib.quote_plus('doctype_facet_hier:"0/Article"') +
                         '&q=*:*&fq=' + urllib.quote('{') + '!' + urllib.quote('type=aqp v=$fq_doctype}') +
                         '&fq_doctype=(' + urllib.quote_plus('doctype_facet_hier:"0/Article"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)
        req.args = MultiDict([('article_sel', 'NO')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +
                         '&error_message=' + 'UNRECOGNIZABLE_VALUE' + '&unprocessed_parameter=' + 'article_sel' + '/', search)

    def test_data_link(self):
        """data_link to property:data"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_link', 'YES'), ('data_and', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('esources:*') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_preprint_link(self):
        """preprint_link to property:eprint"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('preprint_link', 'YES'), ('data_and', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('esources:("EPRINT_HTML")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_open_link(self):
        """open_link to property:OPENACCESS"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('open_link', 'YES'), ('data_and', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("OPENACCESS")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_multiple_link_properties(self):
        """multiple Bumblebee property fields set"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('open_link', 'YES'), ('data_link', 'YES'), ('data_and', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=(' + urllib.quote('esources:*') + ' AND ' +  urllib.quote('property:("OPENACCESS")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_classic_parameters_entry_date(self):
        """test entry date"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)  # no pub date

        req.args = MultiDict([('start_entry_year', "1990"), ('end_entry_year', "1991")])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entdate:["1990-01-01" TO "1991-12-31"]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)  # both years only

        req.args = MultiDict([('start_entry_year', "1990"), ('start_entry_mon', "5"),
                              ('end_entry_year', "1991"), ('end_entry_mon', "9")])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entdate:["1990-05-01" TO "1991-09-30"]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search) # years and months

        req.args = MultiDict([('start_entry_year', "1990"), ('end_entry_year', "1991"), ('end_entry_mon', "10")])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entdate:["1990-01-01" TO "1991-10-31"]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search) # no start mon

        req.args = MultiDict([('start_entry_year', "1990"), ('start_entry_mon', "5"), ('end_entry_year', "1991")])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entdate:["1990-05-01" TO "1991-12-31"]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search) # no end mon

        req.args = MultiDict([('start_entry_year', "1990"), ('start_entry_mon', "5")])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entdate:["1990-05-01" TO "{}"]'.format(datetime.now().strftime("%Y-%m-%d"))) +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search) # no end
        req.args = MultiDict([('end_entry_year', "1991"), ('end_entry_mon', "10")])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entdate:["0001-01-01" TO "1991-10-31"]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search) # no start

        req.args = MultiDict([('start_entry_year', "1990"), ('start_entry_mon', "5"), ('start_entry_day', "6"),
                              ('end_entry_year', "1991"), ('end_entry_mon', "9"), ('end_entry_day', "10")])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entdate:["1990-05-06" TO "1991-09-10"]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search) # years, months, days

        req.args = MultiDict([('start_entry_year', "90"), ('end_entry_year', "10")])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entdate:["1990-01-01" TO "2010-12-31"]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)  # years, months, days

        req.args = MultiDict([('start_entry_year', "25"), ('end_entry_year', "20")])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entdate:["1925-01-01" TO "2020-12-31"]') +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)  # years, months, days

    def test_classic_results_subset(self):
        """test results subset"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)  # no results subset

        req.args = MultiDict([('nr_to_return', 20) , ('start_nr', 1)])
        view = ClassicSearchRedirectView()
        req.args.update(self.append_defaults())
        search = view.translate(req)
        # disabled this for now since it is not implemented, not that it is an error
        # self.assertTrue('error_message' in search)  # both number to return and start index

        req.args = MultiDict([('nr_to_return', 20)])
        view = ClassicSearchRedirectView()
        req.args.update(self.append_defaults())
        search = view.translate(req)
        # self.assertTrue('error_message' in search)  # only number to return

        req.args = MultiDict([('start_nr', 1)])
        view = ClassicSearchRedirectView()
        req.args.update(self.append_defaults())
        search = view.translate(req)
        # self.assertTrue('error_message' in search)  # only start index

    def test_return_req(self):
        """test results subset"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)  # no value

        req.args = MultiDict([('return_req', 'result')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)  # only valid value

        req.args = MultiDict([('return_req', 'form')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # unsuppoprted value for return_req
        self.assertTrue('UNRECOGNIZABLE_VALUE' in search)  # unsuppoprted value for return_req

    def test_jou_pick(self):
        """test jou_pick (refereed)"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)  # no value

        req.args = MultiDict([('jou_pick', 'ALL')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search) # no clause should be specified, defaults to all

        req.args = MultiDict([('jou_pick', 'NO')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('filter_property_fq_property=AND' +
                         '&filter_property_fq_property=property:"refereed"' +
                         '&q=*:*&fq=' + urllib.quote('{') + '!' + urllib.quote('type=aqp v=$fq_property}') +
                         '&fq_property=(' + urllib.quote('property:("refereed")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search) # only refereed

        req.args = MultiDict([('jou_pick', 'EXCL')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('filter_property_fq_property=AND' +
                         '&filter_property_fq_property=property:"not refereed"' +
                         '&q=*:*&fq=' + urllib.quote('{') + '!' + urllib.quote('type=aqp v=$fq_property}') +
                         '&fq_property=(' + urllib.quote('property:("not refereed")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)    # exclude refereed

        req.args = MultiDict([('jou_pick', 'foo')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # invalid value for jou_pick
        self.assertTrue('UNRECOGNIZABLE_VALUE' in search)  # invalid value for jou_pick

    def test_not_processed(self):
        """verify parameters that are not processed show up in message to user

        passes in parameters that are not currently translated
        """
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.args = MultiDict([('aut_syn', 'foo')])
        req.mimetype = None
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('unprocessed_parameter' in search)
        self.assertTrue(urllib.quote('Synonym Replacement') in search)

        req.args = MultiDict([('aut_syn', 'foo'), ('aut_wt', 'bar')])
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('unprocessed_parameter' in search)
        self.assertTrue(urllib.quote('Synonym Replacement') in search)
        self.assertTrue(urllib.quote('Relative Weights') in search)

    def test_qsearch(self):
        """qsearch searches metadata

        used by unfielded form
        """
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('qsearch', 'bIbcOde=2005LRSP....2....4B')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=bibcode%3A%222005LRSP....2....4B%22&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)

        req.args = MultiDict([('qsearch', '2005LRSP....2....4B')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=bibcode%3A%222005LRSP....2....4B%22&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)

        req.args = MultiDict([('qsearch', 'title ads')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=title%3A%22ads%22&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)

        req.args = MultiDict([('qsearch', 'Author:accomazzi')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=author%3A%22accomazzi%22&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)

        req.args = MultiDict([('qsearch', 'Doi:10.5281/zenodo.10505 e')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=doi%3A%2210.5281%2Fzenodo.10505+e%22&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)

        req.args = MultiDict([('qsearch', '10.5281/zenodo.10505 e')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=doi%3A%2210.5281%2Fzenodo.10505+e%22&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)

        req.args = MultiDict([('qsearch', 'Year 2017-2019')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=year%3A2017-2019&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)

        req.args = MultiDict([('qsearch', 'year=2019')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=year%3A2019&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)

        req.args = MultiDict([('qsearch', 'accomazzi 2019')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=accomazzi+2019&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' + '/', search)


    def test_data_and(self):
        """test data_and"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)  # no value

        req.args = MultiDict([('data_and', 'NO'), ('article', 'YES'), ('gif_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=(' +
                         urllib.quote('esources:("PUB_PDF" OR "PUB_HTML")') + ' OR ' + urllib.quote('esources:("ADS_SCAN")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('data_and', 'NO'), ('article', 'YES'), ('gif_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=(' +
                         urllib.quote('esources:("PUB_PDF" OR "PUB_HTML")') + ' OR ' + urllib.quote('esources:("ADS_SCAN")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('data_and', 'YES'), ('article', 'YES'), ('gif_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=(' +
                         urllib.quote('esources:("PUB_PDF" OR "PUB_HTML")') + ' AND ' + urllib.quote('esources:("ADS_SCAN")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('data_and', 'NOT'), ('article', 'YES'), ('gif_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=(NOT ' +
                         urllib.quote('esources:("PUB_PDF" OR "PUB_HTML")') + ' NOT ' + urllib.quote('esources:("ADS_SCAN")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('data_and', 'foo')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # invalid value for data_and
        self.assertTrue('UNRECOGNIZABLE_VALUE' in search)  # invalid value for data_and

    def test_article_link(self):
        """test article_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('article_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' +
                         urllib.quote('esources:("PUB_PDF" OR "PUB_HTML" OR "AUTHOR_PDF" OR "AUTHOR_HTML" OR "ADS_PDF" OR "ADS_SCAN")') +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_gif_link(self):
        """test gif_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('gif_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('esources:("ADS_SCAN")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_article(self):
        """test article"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('article', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('esources:("PUB_PDF" OR "PUB_HTML")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_toc_link(self):
        """test toc_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('toc_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("TOC")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_ref_link(self):
        """test ref_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('ref_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('reference:*') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_citation_link(self):
        """test citation_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('citation_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('citation_count:[1 TO *]') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_associated_link(self):
        """test associated_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('associated_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("ASSOCIATED")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_simb_obj(self):
        """test simb_obj"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('simb_obj', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('data:("simbad")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_ned_obj(self):
        """test ned_obj"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('ned_obj', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('data:("ned")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_pds_link(self):
        """test pds_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('pds_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('data:("PDS")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_aut_note(self):
        """test aut_note"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('aut_note', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("NOTE")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_ar_link(self):
        """test ar_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('ar_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('read_count:[1 TO *]') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_multimedia_link(self):
        """test multimedia_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('multimedia_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("PRESENTATION")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_spires_link(self):
        """test spires_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('spires_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("INSPIRE")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_abstract(self):
        """test abstract"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('data_and', 'YES'), ('abstract', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('abstract:*') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_lib_link(self):
        """test lib_link"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('lib_link', 'YES')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('property:("LIBRARYCATALOG")') + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_error_link(self):
        """test error in data group"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None
        req.args = MultiDict([('data_and', 'YES'), ('abstract', 'foo')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +
                         '&error_message=' + 'UNRECOGNIZABLE_VALUE' + '&unprocessed_parameter=' + 'abstract' + '/', search)

    def test_group_and(self):
        """test group_and"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('group_and', 'ALL')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('group_and', 'NO'), ('group_sel', 'ARI'), ('group_sel', 'ESO/Lib'), ('group_sel', 'HST')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('filter_bibgroup_facet_fq_bibgroup_facet=OR' +
                         '&filter_bibgroup_facet_fq_bibgroup_facet=bibgroup_facet:"ARI"' +
                         '&filter_bibgroup_facet_fq_bibgroup_facet=bibgroup_facet:"ESO/Lib"' +
                         '&filter_bibgroup_facet_fq_bibgroup_facet=bibgroup_facet:"HST"' +
                         '&q=*:*' + '&fq=' + urllib.quote('{') + '!' + urllib.quote('type=aqp v=$fq_bibgroup_facet}') +
                         '&fq_bibgroup_facet=(' + urllib.quote_plus('bibgroup_facet:("ARI" OR "ESO/Lib" OR "HST")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('group_and', 'YES'), ('group_sel', 'ARI'), ('group_sel', 'ESO/Lib'), ('group_sel', 'HST')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('filter_bibgroup_facet_fq_bibgroup_facet=AND' +
                         '&filter_bibgroup_facet_fq_bibgroup_facet=bibgroup_facet:"ARI"' +
                         '&filter_bibgroup_facet_fq_bibgroup_facet=bibgroup_facet:"ESO/Lib"' +
                         '&filter_bibgroup_facet_fq_bibgroup_facet=bibgroup_facet:"HST"' +
                         '&q=*:*' + '&fq=' + urllib.quote('{') + '!' + urllib.quote('type=aqp v=$fq_bibgroup_facet}') +
                         '&fq_bibgroup_facet=(' + urllib.quote_plus('bibgroup_facet:("ARI" AND "ESO/Lib" AND "HST")') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('group_and', 'foo')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +
                         '&error_message=' + 'UNRECOGNIZABLE_VALUE' + '&unprocessed_parameter=' + 'group_and' + '/', search)

        req.args = MultiDict([('group_and', 'YES'), ('group_sel', 'foo')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +
                         '&error_message=' + 'UNRECOGNIZABLE_VALUE' + '&unprocessed_parameter=' + 'group_sel' + '/', search)

        req.args = MultiDict([('group_and', 'YES'), ('group_sel', '')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +
                         '&error_message=' + 'UNRECOGNIZABLE_VALUE' + '&unprocessed_parameter=' + 'group_sel' + '/', search)

    def test_sort(self):
        """test sort"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict()
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('sort', 'SCORE')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('score desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('sort', 'foo')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&format=SHORT' + '&error_message=' + 'UNRECOGNIZABLE_VALUE' + '&unprocessed_parameter=' + 'sort' + '/', search)

    def test_arxiv_sel(self):
        """test arxiv_sel"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('arxiv_sel', 'cs'), ('arxiv_sel', 'physics')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=keyword:(' + urllib.quote('"computer science" OR "physics"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('arxiv_sel', '')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  \
                         '&error_message=' + 'UNRECOGNIZABLE_VALUE' + '&unprocessed_parameter=' + 'arxiv_sel' + '/', search)

        req.args = MultiDict([('arxiv_sel', 'ADS')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  \
                         '&error_message=' + 'UNRECOGNIZABLE_VALUE' + '&unprocessed_parameter=' + 'arxiv_sel' + '/', search)

        req.args = MultiDict([('arxiv_sel', 'astro-ph'), ('arxiv_sel', 'cond-mat'), ('arxiv_sel', 'cs'), ('arxiv_sel', 'gr-qc'),
                              ('arxiv_sel', 'hep-ex'), ('arxiv_sel', 'hep-lat'), ('arxiv_sel', 'hep-ph'), ('arxiv_sel', 'hep-th'),
                              ('arxiv_sel', 'math'), ('arxiv_sel', 'math-ph'), ('arxiv_sel', 'nlin'), ('arxiv_sel', 'nucl-ex'),
                              ('arxiv_sel', 'nucl-th'), ('arxiv_sel', 'physics'), ('arxiv_sel', 'quant-ph'), ('arxiv_sel', 'q-bio')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=property:(' + urllib.quote("EPRINT_OPENACCESS") + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        # 3/19/2019 remove the warning, as per Alberto.
        # req.args = MultiDict([('db_key', 'AST'), ('arxiv_sel', 'cs'), ('arxiv_sel', 'physics')])
        # req.args.update(self.append_defaults())
        # view = ClassicSearchRedirectView()
        # search = view.translate(req)
        # self.assertEqual('filter_database_fq_database=OR' +
        #                  '&filter_database_fq_database=database:"astronomy"' +
        #                  '&q=*:*&fq=%7B!type%3Daqp%20v%3D%24fq_database%7D&fq_database=(database%3A%22astronomy%22)' +
        #                  '&sort=' + urllib.quote('date desc, bibcode desc') +
        #                  '&warning_message=' + urllib.quote('when the astronomy or physics databases are selected, the arXiv selection is ignored') + '/',
        #                  search)  # astronomy only

    def test_ref_stems(self):
        """test ref_stems"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('ref_stems', 'ApJ, AJ, AAS')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=bibstem:(' + urllib.quote('"ApJ"') + ' OR ' +  urllib.quote('"AJ"') + ' OR ' +  urllib.quote('"AAS"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('ref_stems', '-AAS')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=-bibstem:(' + urllib.quote('"AAS"')  + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('ref_stems', '-AAS, -arXiv')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=-bibstem:(' + urllib.quote('"AAS"') + ' OR ' +  urllib.quote('"arXiv"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('ref_stems', 'arxiv, -AAS, EPJWC')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=bibstem:(' + urllib.quote('"arxiv"') + ' OR ' +  urllib.quote('"EPJWC"') + ') AND ' +
                         '-bibstem:(' + urllib.quote('"AAS"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

        req.args = MultiDict([('ref_stems', 'A&A, GCN1, -CLic2, JPhy3, -JPhy4')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=bibstem:(' + urllib.quote('"A&A"') + ' OR ' +  urllib.quote('"GCN1"') + ' OR ' +  urllib.quote('"JPhy3"') + ') AND ' +
                         '-bibstem:(' + urllib.quote('"CLic2"') + ' OR ' +  urllib.quote('"JPhy4"') + ')' +
                         '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +  '/', search)

    def test_myads_query(self):
        """test query_type"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        # Daily arXiv query
        req.args = MultiDict([('query_type', 'PAPERS'), ('db_key', 'DAILY_PRE'), ('qform', 'PRE'),
                              ('arxiv_sel', 'astro-ph'), ('start_year', '2019'),
                              ('start_entry_day', '15'), ('start_entry_mon', '10'), ('start_entry_year', '2019'),
                              ('end_entry_day', '16'), ('end_entry_mon', '10'), ('end_entry_year', '2019'),
                              ('title', '*+"nuclear star cluster"')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('bibstem:arxiv ((arxiv_class:astro-ph.*) OR +"nuclear star cluster") entdate:["2019-10-15:00:00" TO 2019-10-16] pubdate:[2019-00 TO *]') +
                         '&sort=' + urllib.quote('score desc') + '/', search)

        # Weekly citations query
        req.args = MultiDict([('query_type', 'CITES'), ('db_key', 'ALL'),
                              ('author', 'LOCKHART, KELLY')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('citations(author:"LOCKHART, KELLY")') +
                         '&sort=' + urllib.quote('score desc') +  '/', search)

        # Weekly authors query
        req.args = MultiDict([('query_type', 'PAPERS'), ('db_key', 'AST'),
                              ('author', 'LU, JESSICA\r\nHOSEK, MATTHEW\r\nKEWLEY, LISA\r\nACCOMAZZI, ALBERTO\r\nKURTZ, MICHAEL'),
                              ('start_entry_day', '26'), ('start_entry_mon', '9'), ('start_entry_year', '2019'),
                              ('end_entry_day', '18'), ('end_entry_mon', '10'), ('end_entry_year', '2019'),
                              ('start_year', '2019')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('filter_database_fq_database=OR&filter_database_fq_database=database:"astronomy"&'
                         'q=' + urllib.quote('author:"LU, JESSICA" OR author:"HOSEK, MATTHEW" OR author:"KEWLEY, LISA" OR author:"ACCOMAZZI, ALBERTO" OR author:"KURTZ, MICHAEL" entdate:["2019-09-26:00:00" TO 2019-10-18] pubdate:[2019-00 TO *]') +
                         '&fq=%7B!type%3Daqp%20v%3D%24fq_database%7D&fq_database=(database%3A%22astronomy%22)' +
                         '&sort=' + urllib.quote('score desc') + '/', search)

        # Weekly keyword (recent papers) query
        req.args = MultiDict([('query_type', 'PAPERS'), ('db_key', 'AST'),
                              ('title', '"nuclear star cluster" OR ADS OR "supermassive black holes" OR M31 OR "Andromeda Galaxy" OR OSIRIS OR IFU'),
                              ('start_entry_day', '26'), ('start_entry_mon', '9'), ('start_entry_year', '2019'),
                              ('end_entry_day', '18'), ('end_entry_mon', '10'), ('end_entry_year', '2019'),
                              ('start_year', '2019')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('filter_database_fq_database=OR&filter_database_fq_database=database:"astronomy"&'
                         'q=' + urllib.quote('"nuclear star cluster" OR ADS OR "supermassive black holes" OR M31 OR "Andromeda Galaxy" OR OSIRIS OR IFU entdate:["2019-09-26:00:00" TO 2019-10-18] pubdate:[2019-00 TO *]') +
                         '&fq=%7B!type%3Daqp%20v%3D%24fq_database%7D&fq_database=(database%3A%22astronomy%22)' +
                         '&sort=' + urllib.quote('entry_date desc') +  '/', search)

        # Weekly keyword (popular papers) query
        req.args = MultiDict([('query_type', 'ALSOREADS'), ('db_key', 'AST'),
                              ('title', '"nuclear star cluster" OR ADS OR "supermassive black holes" OR M31 OR "Andromeda Galaxy" OR OSIRIS OR IFU')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('filter_database_fq_database=OR&filter_database_fq_database=database:"astronomy"&' +
                         'q=' + urllib.quote('trending("nuclear star cluster" OR ADS OR "supermassive black holes" OR M31 OR "Andromeda Galaxy" OR OSIRIS OR IFU)') +
                         '&fq=%7B!type%3Daqp%20v%3D%24fq_database%7D&fq_database=(database%3A%22astronomy%22)' +
                         '&sort=' + urllib.quote('score desc') + '/', search)

        # Weekly keyword (most cited) query
        req.args = MultiDict([('query_type', 'REFS'), ('db_key', 'AST'),
                              ('title', '"nuclear star cluster" OR ADS OR "supermassive black holes" OR M31 OR "Andromeda Galaxy" OR OSIRIS OR IFU')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('filter_database_fq_database=OR&filter_database_fq_database=database:"astronomy"&' +
                         'q=' + urllib.quote('useful("nuclear star cluster" OR ADS OR "supermassive black holes" OR M31 OR "Andromeda Galaxy" OR OSIRIS OR IFU)') +
                         '&fq=%7B!type%3Daqp%20v%3D%24fq_database%7D&fq_database=(database%3A%22astronomy%22)' +
                         '&sort=' + urllib.quote('score desc') + '/', search)

    def test_myads_query_error(self):
        """test query_type"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        # undefined query_type
        req.args = MultiDict([('query_type', 'error')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' +  '&error_message=UNRECOGNIZABLE_VALUE/', search)

        # missing params
        req.args = MultiDict([('query_type', 'ALSOREADS')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' +  '&error_message=MISSING_REQUIRED_PARAMETER/', search)

        # when both author and title is supplied to query_type == 'PAPER' and db_key == 'AST'
        req.args = MultiDict([('query_type', 'PAPER'),
                              ('author', 'LU, JESSICA\r\nHOSEK, MATTHEW\r\nKEWLEY, LISA\r\nACCOMAZZI, ALBERTO\r\nKURTZ, MICHAEL'),
                              ('title', '"nuclear star cluster" or ADS or "supermassive black holes" or M31 or "Andromeda Galaxy" or OSIRIS or IFU'),
                              ('start_year', '2019')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' +  '&error_message=UNRECOGNIZABLE_VALUE/', search)

    def test_translate_to_ignore(self):
        """ test translate_to_ignore"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('lpi_query', 'NO')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +
                         '&unprocessed_parameter=lpi_query/', search)

    def test_translate_weights(self):
        """ test translate_weights"""
        req = Request('get', 'http://test.test?')
        req.prepare()
        req.mimetype = None

        req.args = MultiDict([('aut_syn', 'NO')])
        req.args.update(self.append_defaults())
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*' + '&sort=' + urllib.quote('date desc, bibcode desc') + '&format=SHORT' +
                         '&unprocessed_parameter=Synonym%20Replacement/', search)


if __name__ == '__main__':
    unittest.main(verbosity=2)
