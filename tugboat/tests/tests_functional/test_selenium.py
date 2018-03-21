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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from httmock import urlmatch, HTTMock
from selenium.webdriver.firefox.options import Options as OptionsFF
from selenium.webdriver.chrome.options import Options as OptionsChrom

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
        # Firefox
        options_firefox = OptionsFF()
        options_firefox.add_argument('-headless')
        self.firefox_driver = webdriver.Firefox(firefox_options=options_firefox)
        # Chrome
        options_chrome = OptionsChrom()
        options_chrome.add_argument('-headless')
        self.chrome_driver = webdriver.Chrome(chrome_options=options_chrome)

    def tearDown(self):
        self.firefox_driver.close()
        self.chrome_driver.close()

    def url_for(self, view):
        """
        Get the url for a live server with the relevant view
        """
        return '{}/{}'.format(self.get_server_url(), view)

    def test_server_firefox(self):
        """
        Test selenium/live server setup is working
        """
        url = self.url_for('index')

        self.firefox_driver.get(url)
        self.assertIn(
            'tugboat test',
            self.firefox_driver.title.lower(),
            msg='Title is: {}'.format(self.firefox_driver.title)
        )

    def test_server_chrome(self):
        """
        Test selenium/live server setup is working
        """
        url = self.url_for('index')

        self.chrome_driver.get(url)
        self.assertIn(
            'tugboat test',
            self.chrome_driver.title.lower(),
            msg='Title is: {}'.format(self.chrome_driver.title)
        )

    def test_post_bibcodes_firefox(self):
        """
        Test posting bibcodes redirects to bumblebee
        """
        url = self.url_for('index')

        self.firefox_driver.get(url)

        text_area = self.firefox_driver.find_element_by_name('mytextarea')
        text_area.clear()
        text_area.send_keys('2015arXiv150701293E')
        text_area.send_keys(Keys.ENTER)
        text_area.send_keys('2015A&C....10...61E')

        form = self.firefox_driver.find_element_by_name('submit')
        form.submit()
        with HTTMock(store_200):
            form = self.firefox_driver.find_element_by_name('submit')
            form.submit()

            try:
                WebDriverWait(self.firefox_driver, 10).until(EC.title_contains('Tugboat'))
            except TimeoutException:
                self.fail('Redirect did not succeed')

    def test_post_bibcodes_chrome(self):
        """
        Test posting bibcodes redirects to bumblebee
        """
        url = self.url_for('index')

        self.chrome_driver.get(url)

        text_area = self.chrome_driver.find_element_by_name('mytextarea')
        text_area.clear()
        text_area.send_keys('2015arXiv150701293E')
        text_area.send_keys(Keys.ENTER)
        text_area.send_keys('2015A&C....10...61E')

        form = self.chrome_driver.find_element_by_name('submit')
        form.submit()
        with HTTMock(store_200):
            form = self.chrome_driver.find_element_by_name('submit')
            form.submit()

            try:
                WebDriverWait(self.chrome_driver, 10).until(EC.title_contains('Tugboat'))
            except TimeoutException:
                self.fail('Redirect did not succeed')

    def test_redirect_search_firefox(self):
        """
        end to end test of search redirect
        """
        url = self.url_for('classicSearchRedirect?object=object')

        self.firefox_driver.get(url)
        try:
            WebDriverWait(self.firefox_driver, 10).until(EC.title_contains('ADS'))
        except TimeoutException:
            self.fail('Redirect did not succeed')

    def test_redirect_search_chrome(self):
        """
        end to end test of search redirect
        """
        url = self.url_for('classicSearchRedirect?object=object')

        self.chrome_driver.get(url)
        try:
            WebDriverWait(self.chrome_driver, 10).until(EC.title_contains('ADS'))
        except TimeoutException:
            self.fail('Redirect did not succeed')

if __name__ == '__main__':
    unittest.main(verbosity=2)
