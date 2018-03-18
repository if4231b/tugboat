# coding: utf-8
"""
Test webservices
"""

import sys
import os
PROJECT_HOME = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../../'))
sys.path.append(PROJECT_HOME)

import unittest

from flask.ext.testing import LiveServerTestCase
from tugboat.app import create_app
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from httmock import urlmatch, HTTMock


@urlmatch(netloc=r'*')
def store_200(url, request):
    return {
        'status_code': 200,
        'content': {'qid': 'adsf1234', 'query': 'q', 'numfound': 1}
    }

class TestBumblebeeView(LiveServerTestCase):
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
        app_.config['TESTING'] = True
        app_.config['LIVESERVER_PORT'] = 8943
        return app_

    def setUp(self):
        options = Options()
        options.add_argument('-headless')
        self.driver = webdriver.Firefox(firefox_options=options)

    def tearDown(self):
        self.driver.close()

    def url_for(self, view):
        """
        Get the url for a live server with the relevant view
        """
        return '{}/{}'.format(self.get_server_url(), view)

    def test_server(self):
        """
        Test selenium/live server setup is working
        """
        url = self.url_for('index')

        self.driver.get(url)
        self.assertIn(
            'tugboat test',
            self.driver.title.lower(),
            msg='Title is: {}'.format(self.driver.title)
        )

    def test_post_bibcodes(self):
        """
        Test posting bibcodes redirects to bumblebee
        """
        url = self.url_for('index')

        self.driver.get(url)

        text_area = self.driver.find_element_by_name('mytextarea')
        text_area.clear()
        text_area.send_keys('2015arXiv150701293E')
        text_area.send_keys(Keys.ENTER)
        text_area.send_keys('2015A&C....10...61E')

        form = self.driver.find_element_by_name('submit')
        form.submit()
        with HTTMock(store_200):
            form = self.driver.find_element_by_name('submit')
            form.submit()

            try:
                WebDriverWait(self.driver, 10).until(EC.title_contains('ADS'))
            except TimeoutException:
                self.fail('Redirect did not succeed')

    def test_redirect_search(self):
        """
        end to end test of search redirect
        """
        url = self.url_for('classicSearchRedirect?object=object')
        self.driver.get(url)
        try:
            WebDriverWait(self.driver, 10).until(EC.title_contains('ADS'))
        except TimeoutException:
            self.fail('Redirect did not succeed')

if __name__ == '__main__':
    unittest.main(verbosity=2)
