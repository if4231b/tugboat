
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

from tugboat.views import ClassicSearchRedirectView

class TestSearchParametersTranslation(TestCase):
    """
    Test translation of each of the classic search parameters

    """

    def test_authors(self):
        """authors: single, multple, quoted,  and/or"""

        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        view = ClassicSearchRedirectView()
        empty_search = view.translate(req)
        self.assertEqual('q=*:*', empty_search, 'author test')  # no authors

        req.args = {'author': urllib.quote('Huchra,+John')}
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        # parentheses are not urlencoded
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John"') + ')', 
                         author_search) # single author no quotes

        req.args = {'author': urllib.quote('"Huchra,+John"')}
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John"') + ')', 
                         author_search) # single author with quotes

        req.args = {'author': urllib.quote('Huchra, John\r\nMacri, Lucas M.')}
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" AND "Macri, Lucas M."') + ')',
                         author_search) # authors, newline separator

        req.args = {'author': urllib.quote('Huchra,+John;Macri,+Lucas+M.')}
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" AND "Macri, Lucas M."') + ')',
                         author_search) # authors, semicolon separator

        req.args = {'author': urllib.quote('Huchra,+John'), 'aut_xct': 'YES'}
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('=author:') + '(' + urllib.quote('"Huchra, John"') + ')', 
                         author_search) # author with exact match

        req.args = {'author': urllib.quote('Huchra,+John;Macri,+Lucas+M.'), 'aut_logic':'OR'}
        view = ClassicSearchRedirectView()
        author_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" OR "Macri, Lucas M."') + ')', 
                         author_search) # authors with or



    def test_object(self):
        """object: single, multple, etc"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {'object': urllib.quote('M31')}
        view = ClassicSearchRedirectView()
        object_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('M31') + ')', object_search) # single object

        req.args = {'object': urllib.quote('M31\r\nM32')}
        view = ClassicSearchRedirectView()
        object_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('M31 AND M32') + ')',
                         object_search) # objects, newline separator

        req.args = {'object': urllib.quote('M31;M32;M33')}
        view = ClassicSearchRedirectView()
        object_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('M31 AND M32 AND M33') + ')',
                         object_search) # object, semicolor separator

    def test_title(self):
        """title field"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {'title': urllib.quote('M31')}
        view = ClassicSearchRedirectView()
        object_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('title:') + '(' + urllib.quote('M31') + ')', object_search) # single object
        
    def test_text(self):
        """text search"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {'text': urllib.quote('M31')}
        view = ClassicSearchRedirectView()
        object_search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('abs:') + '(' + urllib.quote('M31') + ')', object_search) # single object
        
    def test_pubdate(self):
        """test pubdate"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*', search)  # no pub date

        req.args = {'start_year': 1990, 'end_year': 1991}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-01 TO 1991-12]'), search)  # both years only

        req.args = {'start_year': 1990, 'start_mon': 5, 'end_year': 1991, 'end_mon': 10}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO 1991-10]'), search) # years and months
 
        req.args = {'start_year': 1990, 'end_year': 1991, 'end_mon': 10}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-01 TO 1991-10]'), search) # no start mon
       
        req.args = {'start_year': 1990, 'start_mon': 5, 'end_year': 1991}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO 1991-12]'), search) # no end mon

        req.args = {'start_year': 1990, 'start_mon': 5}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        n = datetime.now()
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO {:04d}-{:02d}]'.format(n.year, n.month)), search) # no end
        req.args = {'end_year': 1991, 'end_mon': 10}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[0000-01 TO 1991-10]'), search) # no start

    def test_database(self):
        """database can be astronomy or physics 

        not clear how to test with more than one database set"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'db_key': 'AST'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_database}&fq_database=(database:"astronomy")'),
                         search) # astro only


        req.args = {'db_key': 'PHY'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_database}&fq_database=(database:"physics")'),
                         search) # physics only


        req.args = {'db_key': 'GEN'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_database}&fq_database=(database:"general")'),
                         search) # general only

    def test_article_sel(self):
        """article_sel to property:article"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'article_sel': 'YES'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"article")'), search)
 

    def test_data_link(self):
        """data_link to property:data"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'data_link': 'YES'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"data")'), search)

    def test_preprint_link(self):
        """preprint_link to property:eprint"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'preprint_link': 'YES'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"eprint")'), search)

    def test_note_link(self):
        """aut_note to property:note"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'aut_note': 'YES'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"note")'), search)

    def test_open_link(self):
        """open_link to property:OPENACCESS"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'open_link': 'YES'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"OPENACCESS")'),
                         search)
 
    def test_multiple_link_properties(self):
        """multiple Bumblebee property fields set"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'article_sel': 'YES', 'data_link': 'YES' }
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        # should comparison permit fq clauses to be in different order?
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"data")') + 
                         '&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"article")'),
                         search)

    def test_classic_parameters_entry_date(self):
        """test entry date"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*', search)  # no pub date

        req.args = {'start_entry_year': 1990, 'end_entry_year': 1991}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-01-01 TO 1991-12-31]'), search)  # both years only

        req.args = {'start_entry_year': 1990, 'start_entry_mon': 5, 'end_entry_year': 1991, 'end_entry_mon': 9}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-05-01 TO 1991-09-30]'), search) # years and months
 
        req.args = {'start_entry_year': 1990, 'end_entry_year': 1991, 'end_entry_mon': 10}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-01-01 TO 1991-10-31]'), search) # no start mon
       
        req.args = {'start_entry_year': 1990, 'start_entry_mon': 5, 'end_entry_year': 1991}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-05-01 TO 1991-12-31]'), search) # no end mon

        req.args = {'start_entry_year': 1990, 'start_entry_mon': 5}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        n = datetime.now()
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-05-01 TO {:04d}-{:02d}-{:02d}]'.format(n.year, n.month, n.day)), search) # no end
        req.args = {'end_entry_year': 1991, 'end_entry_mon': 10}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[0000-01-01 TO 1991-10-31]'), search) # no start

        req.args = {'start_entry_year': 1990, 'start_entry_mon': 5, 'start_entry_day': 6,
                    'end_entry_year': 1991, 'end_entry_mon': 9, 'end_entry_day': 10}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=' + urllib.quote('entry_date:[1990-05-06 TO 1991-09-10]'), search) # years, months, days

    def test_classic_results_subset(self):
        """test results subset"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*', search)  # no results subset

        req.args = {'nr_to_return': 20 , 'start_nr': 1}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # both number to return and start index

        req.args = {'nr_to_return': 20 }
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # only number to return
        
        req.args = {'start_nr': 1}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # only start index

    def test_return_req(self):
        """test results subset"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*', search)  # no value

        req.args = {'return_req': 'result'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*', search)  # only valid value

        req.args = {'return_req': 'form'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # unsuppoprted value for return_req
        self.assertTrue('form' in search)  # unsuppoprted value for return_req

    def test_jou_pick(self):
        """test jou_pick (refereed)"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*', search)  # no value

        req.args = {'jou_pick': 'ALL'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*', search) # no clause should be specified, defaults to all

        req.args = {'jou_pick': 'NO'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_property}&fq_property=(property:"refereed")'), search)  # only refereed

        req.args = {'jou_pick': 'EXCL'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_property}&fq_property=(property:"notrefereed")'), search)  # exclude refereed

        req.args = {'jou_pick': 'foo'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('error_message' in search)  # invalid value for jou_pick
        self.assertTrue('foo' in search)  # invalid value for jou_pick

    def test_not_processed(self):
        """verify parameters that are not processed show up in message to user

        passes in parameters that are not currently translated
        """
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.args = {'aff_logic': 'foo'}
        req.mimetype = None
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('unprocessed_parameter' in search)
        self.assertTrue('aff_logic' in search)

        req.args = {'aff_logic': 'foo', 'full_logic': 'bar'}
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertTrue('unprocessed_parameter' in search)
        self.assertTrue('aff_logic' in search)
        self.assertTrue('full_logic' in search)

    def test_qsearch(self):
        """qsearch searches metadata

        not used by long classic form
        """
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.args = {'qsearch': 'foo'}
        req.mimetype = None
        view = ClassicSearchRedirectView()
        search = view.translate(req)
        self.assertEqual('q=foo&sort=' + urllib.quote('classic_factor desc, bibcode desc'), search)

        
if __name__ == '__main__':
    unittest.main(verbosity=2)
