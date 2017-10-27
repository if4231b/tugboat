
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

class TestSearchParameters(TestCase):
    """
    Test each of the possble classic search parameters

    Most test are for authors because the application code uses the same libraries for all the fields
    """

    def test_classic_parameters_authors(self):
        """authors: single, multple, quoted,  and/or"""

        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        empty_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=*:*', empty_search, 'author test')  # no authors

        req.args = {'author': urllib.quote('Huchra,+John')}
        author_search = ClassicSearchRedirectView.convert_search(req)
        # parentheses are not urlencoded
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John"') + ')', 
                         author_search) # single author no quotes

        req.args = {'author': urllib.quote('"Huchra,+John"')}
        author_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John"') + ')', 
                         author_search) # single author with quotes

        req.args = {'author': urllib.quote('Huchra, John\r\nMacri, Lucas M.')} 
        author_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" AND "Macri, Lucas M."') + ')',
                         author_search) # authors, newline separator

        req.args = {'author': urllib.quote('Huchra,+John;Macri,+Lucas+M.')}
        author_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" AND "Macri, Lucas M."') + ')',
                         author_search) # authors, semicolon separator

        req.args = {'author': urllib.quote('Huchra,+John'), 'aut_xct': 'YES'}
        author_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('=author:') + '(' + urllib.quote('"Huchra, John"') + ')', 
                         author_search) # author with exact match

        req.args = {'author': urllib.quote('Huchra,+John;Macri,+Lucas+M.'), 'aut_logic':'OR'}
        author_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('author:') + '(' + urllib.quote('"Huchra, John" OR "Macri, Lucas M."') + ')', 
                         author_search) # authors with or



    def test_classic_parameters_object(self):
        """object: single, multple, etc"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {'object': urllib.quote('M31')}
        object_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('M31') + ')', object_search) # single object

        req.args = {'object': urllib.quote('M31\r\nM32')}
        object_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('M31 AND M32') + ')', 
                         object_search) # objects, newline separator

        req.args = {'object': urllib.quote('M31;M32;M33')}
        object_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('object:') + '(' + urllib.quote('M31 AND M32 AND M33') + ')', 
                         object_search) # object, semicolor separator

    def test_classic_parameters_title(self):
        """title field"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {'title': urllib.quote('M31')}
        object_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('title:') + '(' + urllib.quote('M31') + ')', object_search) # single object
        
    def test_classic_parameters_text(self):
        """text search"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {'text': urllib.quote('M31')}
        object_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('abs:') + '(' + urllib.quote('M31') + ')', object_search) # single object
        

    def test_classic_parameters_pubdate(self):
        """test pubdate"""
        req = Request('get', 'http://test.test?') 
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        req.args = {}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=*:*', search)  # no pub date

        req.args = {'start_year': 1990, 'end_year': 1991}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-01 TO 1991-12]'), search)  # both years only

        req.args = {'start_year': 1990, 'start_mon': 5, 'end_year': 1991, 'end_mon': 10}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO 1991-10]'), search) # years and months
 
        req.args = {'start_year': 1990, 'end_year': 1991, 'end_mon': 10}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-01 TO 1991-10]'), search) # no start mon
       
        req.args = {'start_year': 1990, 'start_mon': 5, 'end_year': 1991}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO 1991-12]'), search) # no end mon

        req.args = {'start_year': 1990, 'start_mon': 5}
        search = ClassicSearchRedirectView.convert_search(req)
        n = datetime.now()
        self.assertEqual('q=' + urllib.quote('pubdate:[1990-05 TO {:04d}-{:02d}]'.format(n.year, n.month)), search) # no end
        req.args = {'end_year': 1991, 'end_mon': 10}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=' + urllib.quote('pubdate:[0000-01 TO 1991-10]'), search) # no start

    def test_classic_parameters_database(self):
        """database can be astronomy or physics 

        not clear how to test with more than one database set"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'db_key': 'AST'}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_database}&fq_database=(database:"astronomy")'),
                         search) # astro only


        req.args = {'db_key': 'PHY'}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_database}&fq_database=(database:"physics")'),
                         search) # physics only


        req.args = {'db_key': 'GEN'}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_database}&fq_database=(database:"general")'),
                         search) # general only

    def test_classic_article_sel(self):
        """article_sel to property:article"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'article_sel': 'YES'}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"article")'), search)
 

    def test_classic_data_link(self):
        """data_link to property:data"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'data_link': 'YES'}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"data")'), search)

    def test_classic_preprint_link(self):
        """preprint_link to property:eprint"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'preprint_link': 'YES'}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"eprint")'), search)

    def test_classic_note_link(self):
        """aut_note to property:note"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'aut_note': 'YES'}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"note")'), search)

    def test_classic_open_link(self):
        """open_link to property:OPENACCESS"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'open_link': 'YES'}
        search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"OPENACCESS")'),
                         search)
 
    def test_multiple_link_properties(self):
        """multiple Bumblebee property fields set"""
        req = Request('get', 'http://test.test?')
        prepped = req.prepare()
        req.mimetype = None
        req.args = {'article_sel': 'YES', 'data_link': 'YES' }
        search = ClassicSearchRedirectView.convert_search(req)
        # should comparison permit fq clauses to be in different order?
        self.assertEqual('q=*:*&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"data")') + 
                         '&fq=' + urllib.quote('{!type=aqp v=$fq_doctype}&fq_doctype=(doctype:"article")'),
                         search)

        
        
if __name__ == '__main__':
    unittest.main(verbosity=2)
