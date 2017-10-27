# encoding: utf-8
"""
Views
"""

from utils import get_post_data
from client import client
from flask import redirect, current_app, request, abort
from flask.ext.restful import Resource
from webargs import fields
from webargs.flaskparser import parser
import urllib
from datetime import datetime

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

    Where possible, returned query should be human readable and illustrate what a good query looks like
    """
    def get(self):
        """

        """
        current_app.logger.info('Classic search redirect received data, headers: {}'.format(request.headers))
        # data = get_post_data(request)
        bbb_url=current_app.config['BUMBLEBEE_URL']
        bbb_query = self.convert_search(request)
        return redirect(bbb_url + bbb_query, code=302)        

    @staticmethod
    def convert_search(request):
        """
        Convert classic search parameters to bumblebee
        """

        # schema for params
        api = {
            'article_sel': fields.Str(required=False),
            'aut_logic': fields.Str(required=False),
            'aut_note': fields.Str(required=False),
            'aut_xct': fields.Str(required=False),
            'author': fields.Str(required=False),
            'data_link': fields.Str(required=False),
            'db_key': fields.Str(required=False),
            'end_mon': fields.Integer(required=False),
            'end_year': fields.Integer(required=False),
            'obj_logic': fields.Str(required=False),
            'object': fields.Str(required=False),
            'open_link': fields.Str(required=False),
            'preprint_link': fields.Str(required=False),
            'start_mon': fields.Integer(required=False),
            'start_year': fields.Integer(required=False),
            'text': fields.Str(required=False),
            'txt_logic': fields.Str(required=False),
            'title': fields.Str(required=False),
            'ttl_logic': fields.Str(required=False),
            }
        args = parser.parse(api, request)

        connector = ' '
        search = ClassicSearchRedirectView.convert_authors(args)
        search += ClassicSearchRedirectView.convert_typical(args, 'object', 'object')
        search += ClassicSearchRedirectView.convert_typical(args, 'title', 'title')
        search += ClassicSearchRedirectView.convert_typical(args, 'text', 'abs')
        search += ClassicSearchRedirectView.convert_pubdate(args)

        # filters holds an array of filter querys, 'fq=' added below
        filters = ClassicSearchRedirectView.convert_database(args)
        # add more filters here
        filters += ClassicSearchRedirectView.convert_property_filters(args)

        clauses = '' 
        # add more clauses here

        for key in args:
            # handle remaining query terms
            pass

        if len(search) == 0:
            search = '*:*'
        solr_query = 'q=' + search

        if len(clauses) > 0:
            solr_query += clauses

        if len(filters) > 0:
            solr_query += '&fq=' + '&fq='.join(filters)
        return solr_query


    @staticmethod 
    def author_exact(args):
        """given an aut_xct value, is it true"""
        value = args.get('aut_xct')
        if value:
            if 'YES' == str(value).upper():
                return True
        return False


    @staticmethod
    def get_logic(classic_param, args):
        """given a logic parameter, return its value canonical form"""
        classic_param_to_logic = {'author': 'aut_logic', 'title': 'ttl_logic',
                                  'text': 'txt_logic', 'object': 'obj_logic'}
        if classic_param in args:
            logic_param = classic_param_to_logic[classic_param]
            value = args.get(logic_param)
            if value:
                value = value.upper()
            return value
        return ''


    @staticmethod
    def convert_authors(args):
        """return string with all author search elements

        classic ui allows different and/or between authors and objects so we handle 
        just the author affecting elements here
        """

        connector = ' AND '
        search = ''
        logic = ClassicSearchRedirectView.get_logic('author', args)
        exact = ClassicSearchRedirectView.author_exact(args)
        if logic == 'OR':
            connector = ' OR '
        author_field = 'author:'
        if exact:
            author_field = '=author:'
        # one lone parameter should hold all authors from classic
        authors_str = args.get('author')
        if authors_str:
            authors = ClassicSearchRedirectView.classic_field_to_array(authors_str)
            search += urllib.quote(author_field) + '('
            for author in authors:
                search += urllib.quote(author + connector)
            search = search[:-len(urllib.quote(connector))]  # remove final
            search += ')'
        return search


    @staticmethod
    def convert_typical(args, classic_param, bbb_param):
        """return string with all search elements

        returned string should strive for human readability and use prefered query format
        """
        connector = ' AND '
        search = ''
        logic = ClassicSearchRedirectView.get_logic(classic_param, args)
        if logic == 'OR':
            connector = ' OR '
        # one lone parameter should hold all authors from classic
        classic_str = args.get(classic_param)
        if classic_str:
            terms = ClassicSearchRedirectView.classic_field_to_array(classic_str)
            search += urllib.quote(bbb_param + ':') + '('
            for term in terms:
                search += urllib.quote(term + connector)
            search = search[:-len(urllib.quote(connector))]  # remove final connector
            search += ')'
        return search


    @staticmethod
    def convert_pubdate(args):
        """return string with pubdate element

        for pubdate date search, only start or end need be specified
        at least one start year or end year must be provided
        unlike entrdy date search, negitive offsets are not supported
        in classic, 2 digit years were permitted
        bumblebee example: pubdate:[1990-01 TO 1990-02]
        """
        start_year = args.get('start_year')
        end_year = args.get('end_year')
        if start_year is None and end_year is None:
            return ''
        
        start_month = args.get('start_mon')
        end_month = args.get('end_mon')

        if start_year is None:
            start_year = 0
        if start_month is None:
            start_month = 1

        tmp = datetime.now()
        if end_year is None:
            end_year = tmp.year
            if end_month is None:
                end_month = tmp.month
        else:
            if end_month is None:
                end_month = 12

        # Y10k problem, but for 2 digit years we want to be clear what years we are searching
        search = 'pubdate' + urllib.quote(':[{:04d}-{:02d} TO {:04d}-{:02}]'.format(start_year, start_month,
                                                                                    end_year, end_month))
        return search
        

    @staticmethod
    def convert_database(args):
        """return string with database element

        only support for ast and phy, bbb does not support arxiv value, classic does not support general
        no support to select multiple dbs
        """

        db = args.get('db_key')
        filter = []
        classic_db_to_bbb = {'AST': 'astronomy', 'GEN': 'general', 'PHY': 'physics'}
        if db:
            bbb_db = classic_db_to_bbb.get(db, None)
            if bbb_db:
                f = '{!type=aqp v=$fq_database}&fq_database=(' + 'database:"{}")'.format(bbb_db)
                filter = [urllib.quote(f)]
            else:
                print 'invalid database from classic {}'.format(db)
        return filter


    @staticmethod
    def convert_property_filters(args):
        """filter query for property 

        several search fields translate to a Bumblebee filter query with property
        """
        to_bbb_property = {'article_sel': 'article', 'aut_note': 'note', 'data_link': 'data',
                           'open_link': 'OPENACCESS', 'preprint_link': 'eprint'}
        clauses = []
        for key in to_bbb_property.keys():
            if str(args.get(key)).upper() == 'YES':
                value = to_bbb_property[key]
                clauses += [urllib.quote('{{!type=aqp v=$fq_doctype}}&fq_doctype=(doctype:"{}")'.format(to_bbb_property.get(key)))]
        return clauses
            

    @staticmethod
    def classic_field_to_array(value):
        """ convert authors or objects from classic to list"""
        value = urllib.unquote(value)
        value = value.replace('\r\n', ';')
        values = value.split(';')
        for i in range(0, len(values)):
            values[i] = values[i].replace('+', ' ')
            if ' ' in values[i] and (values[i].startswith('"') and values[i].endswith('"')) is False:
                # value has space and is not already surrounded by double quotes so we add quotes
                values[i] = '"' + values[i] + '"'
        return values


    
    
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
