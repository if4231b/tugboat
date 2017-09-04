
import sys
import os
PROJECT_HOME = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(PROJECT_HOME)

import unittest
from requests import Request
#from flask.ext.testing import TestCase
from unittest import TestCase

from tugboat.views import ClassicSearchRedirectView

class TestSearchParameters(TestCase):
    """
    Test each of the possble classic search parametrs
    """

    def test_classic_parameters(self):
        # create prepared request to send to convert url code
        req = Request('get', 'http://test.test?author=huchra%2C+john')
        prepped = req.prepare()
        req.args = {}
        req.mimetype = None
        empty_search = ClassicSearchRedirectView.convert_search(req)
        self.assertEqual(empty_search, 'q=*:*', 'author test')

        req.args = {'author': 'huchra%2C+john'}
        req.mimetype = None
        author_search = ClassicSearchRedirectView.convert_search(req)
        print '\n\n' + author_search + '\n\n'
        self.assertEqual(author_search, 'q=author%3A%22huchra%2C%20john', 'author test')

if __name__ == '__main__':
    unittest.main(verbosity=2)
