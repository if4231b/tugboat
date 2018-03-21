# coding: utf-8
"""
Test webservices
"""

import sys
import os
PROJECT_HOME = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(PROJECT_HOME)

import json
import unittest

from flask import url_for
from flask_testing import TestCase
from httmock import urlmatch, HTTMock
from tugboat.app import create_app


@urlmatch(netloc=r'fakeapi\.query$')
def store_200(url, request):
    return {
        'status_code': 200,
        'content': {'qid': 'adsf1234', 'query': 'q', 'numfound': 1}
    }


@urlmatch(netloc=r'fakeapi\.query$')
def vault_500(url, request):
    return {
        'status_code': 500,
        'content': 'ERROR'
    }


class TestBumblebeeView(TestCase):
    """
    A basic base class for all of the tests here
    """

    def create_app(self):
        """
        Create the wsgi application
        """
        app_ = create_app()
        app_.config['VAULT_QUERY_URL'] = 'http://fakeapi.query'
        app_.config['BUMBLEBEE_URL'] = 'http://devui.adsabs.harvard.edu'
        self.bumblebee_url = app_.config['BUMBLEBEE_URL']
        return app_

    def test_get_redirect_with_qid(self):
        """
        Tests that when you send a list of bibcodes, you get a queryid URL and
        a redirect status code
        """
        url = url_for('bumblebeeview')
        bibcodes = ['bib1', 'bib2', 'bib3', 'bib4']

        with HTTMock(store_200):
            r = self.client.post(url, data=json.dumps(bibcodes))

        self.assertStatus(r, 200)
        self.assertEqual(
            r.json['redirect'],
            self.bumblebee_url + '/#search/q=*%3A*&__qid=adsf1234'
        )

    def test_when_send_empty_or_no_bibcodes(self):
        """
        Just a simple test to check someone actually sends something
        """
        url = url_for('bumblebeeview')
        r = self.client.post(url, data={'fake': 'data'})
        self.assertStatus(r, 400)

    def test_when_vault_query_sends_non_200(self):
        """
        When vault/query returns a non-200 status code
        """
        url = url_for('bumblebeeview')
        bibcodes = ['bib1', 'bib2', 'bib3', 'bib4']

        with HTTMock(vault_500):
            r = self.client.post(url, data=json.dumps(bibcodes))

        self.assertStatus(r, 500)


if __name__ == '__main__':
    unittest.main(verbosity=2)
