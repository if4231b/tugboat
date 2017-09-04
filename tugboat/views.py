# encoding: utf-8
"""
Views
"""

from utils import get_post_data
from client import client
from flask import redirect, current_app, request, abort
from flask.ext.restful import Resource


class IndexView(Resource):
    """
    Return the index page. This is temporary until the app is deployed on its
    own instance.
    """
    def get(self):
        """
        HTTP GET request
        :return: index html page
        """
        return current_app.send_static_file('index.html')


class ClassicSearchRedirectView(Resource):
    """
    End point converts classic search to bumbblebee, returns an http redirect
    """
    def get(self):
        """

        """
        # Setup the data
        current_app.logger.info('Classic search redirect received data, headers: {}'.format(request.headers))
        data = get_post_data(request)
        bbb_url=current_app.config['BUMBLEBEE_URL']
        return redirect(bbb_url, code=302)        

    
class BumblebeeView(Resource):
    """
    End point that is used to forward a search result page from ADS Classic
    to ADS Bumblebee
    """
    def post(self):
        """
        HTTP GET request

        There are two simple steps:
            1. Send a query to myads-service in 'store-query' that contains
               the list of bibcodes in the user's ADS Classic search
            2. Return a URL with the relevant queryid that the user can be
               forwarded to

        When the user clicks the URL, it will use execute-query to run the
        relevant query via Solr's Bigquery.

        Returns:
        302: redirect to the relevant URL

        :return: str
        """

        # Setup the data
        current_app.logger.info('Received data, headers: {}'.format(request.headers))
        data = get_post_data(request)

        if not isinstance(data, list):
            current_app.logger.error(
                'User passed incorrect format: {}, {}'.format(type(data), data)
            )
            abort(400)
        elif not all([isinstance(i, unicode) for i in data]):
            current_app.logger.error(
                'List contains non-unicode characters: {}'.format(data)
            )
            abort(400)

        bigquery_data = {
            'bigquery': ['bibcode\n' + '\n'.join(data)],
            'q': ['*:*'],
            'fq': ['{!bitset}']
        }

        # POST the query
        # https://api.adsabs.harvard.edu/v1/vault/query
        current_app.logger.info('Contacting vault/query')
        r = client().post(
            current_app.config['VAULT_QUERY_URL'],
            data=bigquery_data
        )

        if r.status_code != 200:
            current_app.logger.warning(
                'vault/query returned non-200 exit status: {}'.format(r.text)
            )
            return r.text, r.status_code, r.headers.items()

        # Get back a query id
        current_app.logger.info('vault/query returned: {}'.format(r.json()))
        query_id = r.json()['qid']

        # Formulate the url based on the query id
        redirect_url = '{BBB_URL}/#search/q=*%3A*&__qid={query_id}'.format(
            BBB_URL=current_app.config['BUMBLEBEE_URL'],
            query_id=query_id
        )
        current_app.logger.info(
            'Returning redirect: {}'.format(redirect_url)
        )

        # Return the query id to the user
        return {'redirect': redirect_url}, 200
