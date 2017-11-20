# encoding: utf-8
"""
Views
"""

from utils import get_post_data
from client import client
import traceback
from flask import redirect, current_app, request, abort
from flask.ext.restful import Resource
from webargs import fields
from webargs.flaskparser import parser
import urllib
from datetime import datetime
import calendar

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


class SimpleClassicView(Resource):
    """for testing, show ads page with single input text field"""
    def get(self):
        return current_app.send_static_file('classic_w_BBB_button.html')

class ComplexClassicView(Resource):
    """for testing, show standard ads search page"""
    def get(self):
        return current_app.send_static_file('fielded_classic_w_BBB_button.html')


class TranslationValue():
    """simple singleton container class to hold translation components

    functions that translation specific parameters typically augment the TranslationValue
    """

    # consider adding field for sort order and other args
    def __init__(self):
        self.search = []
        self.filter= []
        self.error_message = []
        self.warning_message = []


class ClassicSearchRedirectView(Resource):
    """
    End point converts classic search to bumbblebee, returns an http redirect

    Where possible, returned query should be human readable and illustrate what a good query looks like
    """

    def __init__(self):
        super(ClassicSearchRedirectView, self).__init__()
        self.translation = TranslationValue()


        # all the parameters from classic
        # typically integer fields must be represented by Field to allow None values
        # some of these need use type fields.List
        self.api = {
            # the following we currently translate
            'article_sel': fields.Str(required=False),
            'aut_logic': fields.Str(required=False),
            'aut_note': fields.Str(required=False),
            'aut_xct': fields.Str(required=False),
            'author': fields.Str(required=False),
            'data_link': fields.Str(required=False),
            'db_key': fields.Str(required=False),
            'end_entry_day': fields.Field(required=False),
            'end_entry_mon': fields.Field(required=False),
            'end_entry_year': fields.Field(required=False),
            'end_mon': fields.Field(required=False),
            'end_year': fields.Field(required=False),
            'jou_pick': fields.Str(required=False),
            'obj_logic': fields.Str(required=False),
            'object': fields.Str(required=False),
            'open_link': fields.Str(required=False),
            'preprint_link': fields.Str(required=False),
            'qsearch': fields.Str(required=False),
            'return_req': fields.Str(required=False),
            'start_entry_day': fields.Field(required=False),
            'start_entry_mon': fields.Field(required=False),
            'start_entry_year': fields.Field(required=False),
            'start_mon': fields.Field(required=False),
            'start_year': fields.Field(required=False),
            'text': fields.Str(required=False),
            'txt_logic': fields.Str(required=False),
            'title': fields.Str(required=False),
            'ttl_logic': fields.Str(required=False),

            # implementations for the following just create errors
            # perhaps because there is no ads/bumbleebee support yet
            'nr_to_return': fields.Field(required=False),
            'start_nr': fields.Field(required=False),

            # and the following are not yet translated
            'ref_stems': fields.Str(required=False),
            'min_score': fields.Str(required=False),
            'data_link': fields.Str(required=False),
            'preprint_link': fields.Str(required=False),
            'abstract': fields.Str(required=False),
            'aut_note': fields.Str(required=False),
            'article_link': fields.Str(required=False),
            'gif_link': fields.Str(required=False),
            'article': fields.Str(required=False),
            'simb_obj': fields.Str(required=False),
            'ned_obj': fields.Str(required=False),
            'gpndb_obj': fields.Str(required=False),
            'lib_link': fields.Str(required=False),
            'mail_link': fields.Str(required=False),
            'toc_link': fields.Str(required=False),
            'pds_link': fields.Str(required=False),
            'multimedia_link': fields.Str(required=False),
            'ref_link': fields.Str(required=False),
            'citation_link': fields.Str(required=False),
            'open_link': fields.Str(required=False),
            'associated_link': fields.Str(required=False),
            'ar_link': fields.Str(required=False),
            'lpi_query': fields.Str(required=False),
            'sim_query': fields.Str(required=False),
            'ned_query': fields.Str(required=False),
            'iau_query': fields.Str(required=False),
            'adsobj_query': fields.Str(required=False),
            'sort': fields.Str(required=False),
            'group_sel': fields.Str(required=False),
            'arxiv_sel': fields.Str(required=False),
            'data_and': fields.Str(required=False),
            'group_and': fields.Str(required=False),
            'data_type': fields.Str(required=False),

            'aut_wt': fields.Field(required=False),
            'obj_wt': fields.Field(required=False),
            'kwd_wt': fields.Field(required=False),
            'ttl_wt': fields.Field(required=False),
            'txt_wt': fields.Field(required=False),
            'full_wt': fields.Field(required=False),
            'aff_wt': fields.Field(required=False),
            'aut_syn': fields.Str(required=False),
            'ttl_syn': fields.Str(required=False),
            'txt_syn': fields.Str(required=False),
            'full_syn': fields.Str(required=False),
            'aff_syn': fields.Str(required=False),
            'aut_wgt': fields.Str(required=False),
            'obj_wgt': fields.Str(required=False),
            'kwd_wgt': fields.Str(required=False),
            'ttl_wgt': fields.Str(required=False),
            'txt_wgt': fields.Str(required=False),
            'full_wgt': fields.Str(required=False),
            'aff_wgt': fields.Str(required=False),
            'aut_sco': fields.Str(required=False),
            'kwd_sco': fields.Str(required=False),
            'ttl_sco': fields.Str(required=False),
            'txt_sco': fields.Str(required=False),
            'full_sco': fields.Str(required=False),
            'aff_sco': fields.Str(required=False),
            'aut_req': fields.Str(required=False),
            'obj_req': fields.Str(required=False),
            'kwd_req': fields.Str(required=False),
            'ttl_req': fields.Str(required=False),
            'txt_req': fields.Str(required=False),
            'full_req': fields.Str(required=False),
            'aff_req': fields.Str(required=False),
            'aut_logic': fields.Str(required=False),
            'obj_logic': fields.Str(required=False),
            'kwd_logic': fields.Str(required=False),
            'ttl_logic': fields.Str(required=False),
            'txt_logic': fields.Str(required=False),
            'full_logic': fields.Str(required=False),
            'aff_logic': fields.Str(required=False),

            }


    def get(self):
        """
        return 302 to bumblebee
        """
        try:
            current_app.logger.info('Classic search redirect received data, headers: {}'.format(request.headers))
            bbb_url=current_app.config['BUMBLEBEE_URL']
            bbb_query = self.translate(request)
            redirect_url = bbb_url + '/#search/'+ bbb_query
            current_app.logger.info('translated classic {} to bumblebee {}, {}'.format(request, bbb_query, redirect_url))
            return redirect(redirect_url, code=302)
        except Exception as e:
            current_app.logger.error(e.message)
            current_app.logger.error(traceback.format_exc())
            return '<html><body><h2>Error translating classic query</h2> ' + e.message + '<p>' + traceback.format_exc() + '<p>' + str(request) + '</body></html>'


    def translate(self, request):
        """
        Convert all classic search related parameters to ads/bumblebee
        """
        args = parser.parse(self.api, request)
        # functions to translate/process specific parameters
        # consider using reflection to obtain this list
        funcs = [self.translate_authors, self.translate_pubdate,
                 self.translate_entry_date, self.translate_results_subset,
                 self.translate_return_req, self.translate_qsearch,
                 self.translate_database, self.translate_property_filters,
                 self.translate_jou_pick
                 ]
        for f in funcs:
            f(args)  # each may contribute to self.translation singleton

        # functions to deal with the simple cases where only parameter name changes
        self.translate_simple(args, 'object', 'object')
        self.translate_simple(args, 'title', 'title')
        self.translate_simple(args, 'text', 'abs')

        # combine translation fragments in self.translation to ads/bumblebee parameter string
        if len(self.translation.search) == 0:
            self.translation.search = ['*:*']
        solr_query = 'q=' + ' ' .join(self.translation.search)
        if len(self.translation.filter) > 0:
            solr_query += '&fq=' + '&fq='.join(self.translation.filter)
        if len(self.translation.error_message) > 0:
            solr_query += '&error_message=' + '&error_message'.join(self.translation.error_message)
        if len(self.translation.warning_message):
            solr_query += '&warning_message=' + '&warning_message'.join(self.translation.warning_message)
        if len(args.keys()):
            # the functions that translate individual parameters use pop to remove parameters from arg list
            # here if there are unprocessed parameters
            # pass their names ot ads/bumblebee
            solr_query += '&unprocessed_parameter=' + urllib.quote('Parameters not processed: ' + ' '.join(args.keys()))

        return solr_query


    @staticmethod 
    def author_exact(args):
        """given an aut_xct value, is it true"""
        value = args.pop('aut_xct', None)
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
            value = args.pop(logic_param, None)
            if value:
                value = value.upper()
            return value
        return ''

    @staticmethod
    def supplied(value):
        """check html parameter to see if it is valid"""
        if value is None or (isinstance(value, basestring) and len(value) == 0):
            return False
        return True

    def translate_authors(self, args):
        """return string with all author search elements

        classic ui allows different and/or between authors and objects so we handle 
        just the author affecting elements here
        """
        connector = ' AND '
        search = ''
        logic = self.get_logic('author', args)
        exact = self.author_exact(args)
        if logic == 'OR':
            connector = ' OR '
        author_field = 'author:'
        if exact:
            author_field = '=author:'
        # one lone parameter should hold all authors from classic
        authors_str = args.pop('author', None)
        if authors_str:
            authors = self.classic_field_to_array(authors_str)
            search += urllib.quote(author_field) + '('
            for author in authors:
                search += urllib.quote(author + connector)
            search = search[:-len(urllib.quote(connector))]  # remove final
            search += ')'
            self.translation.search.append(search)

    def translate_simple(self, args, classic_param, bbb_param):
        """process easy to translate fields like title

        simply change name of parameter and use boolean connector
        """
        connector = ' AND '
        search = ''
        logic = self.get_logic(classic_param, args)
        if logic == 'OR':
            connector = ' OR '
        # one lone parameter should hold all authors from classic
        classic_str = args.pop(classic_param, None)
        if classic_str:
            terms = ClassicSearchRedirectView.classic_field_to_array(classic_str)
            search += urllib.quote(bbb_param + ':') + '('
            for term in terms:
                search += urllib.quote(term + connector)
            search = search[:-len(urllib.quote(connector))]  # remove final connector
            search += ')'
            self.translation.search.append(search)

    def translate_pubdate(self, args):
        """translate string with pubdate element

        for pubdate date search, only start or end need be specified
        at least one start year or end year must be provided
        unlike entry date search, negative offsets are not supported
        in classic, 2 digit years were permitted
        bumblebee example: pubdate:[1990-01 TO 1990-02]
        """

        start_year = args.pop('start_year', None)
        end_year = args.pop('end_year', None)
        if self.supplied(start_year) is False and self.supplied(end_year) is False:
            return
        
        start_month = args.pop('start_mon', None)
        end_month = args.pop('end_mon', None)

        # if start is not provided, use beginning of time
        if not self.supplied(start_year):
            start_year = 0
        if not self.supplied(start_month):
            start_month = 1

        # if end is not provided, use now
        if not self.supplied(end_year):
            tmp = datetime.now()
            end_year = tmp.year
            if not self.supplied(end_month):
                end_month = tmp.month
        else:
            if not self.supplied(end_month):
                end_month = 12

        start_year = int(start_year)
        start_month = int(start_month)
        end_year = int(end_year)
        end_month = int(end_month)
        # Y10k problem, but for 2 digit years we want to be clear what years we are searching
        search = 'pubdate' + urllib.quote(':[{:04d}-{:02d} TO {:04d}-{:02}]'.format(start_year, start_month,
                                                                                    end_year, end_month))
        self.translation.search.append(search)

    def translate_entry_date(self, args):
        """ return string for pubdate element

        like pubdate search, only start on end need be specified
        bumblebee does not yet implement, assume to follow pubdate 
        """
        start_year = args.pop('start_entry_year', None)
        end_year = args.pop('end_entry_year', None)
        if self.supplied(start_year) is False and self.supplied(end_year) is False:
            return  # nothing to do

        start_month = args.pop('start_entry_mon', None)
        start_day = args.pop('start_entry_day', None)
        end_month = args.pop('end_entry_mon', None)
        end_day = args.pop('end_entry_day', None)

        # if start is not provided, use beginning of time
        if not self.supplied(start_year):
            start_year = 0
        if not self.supplied(start_month):
            start_month = 1
        if not self.supplied(start_day):
            start_day = 1

        # if end is not provided, use now
        if not self.supplied(end_year):
            tmp = datetime.now()
            end_year = tmp.year
            if not self.supplied(end_month):
                end_month = tmp.month
            if not self.supplied(end_day):
                end_day = tmp.day
        else:
            if not self.supplied(end_month):
                end_month = 12
            if not self.supplied(end_day):
                # get last day of end month/year
                end_day = calendar.monthrange(end_year, end_month)[1]

        start_year = int(start_year)
        start_month = int(start_month)
        start_day = int(start_day)
        end_year = int(end_year)
        end_month = int(end_month)
        end_day = int(end_day)
        search = 'entry_date' + \
            urllib.quote(':[{:04d}-{:02d}-{:02d} TO {:04d}-{:02}-{:02d}]'.format(start_year, start_month, start_day,
                                                                                 end_year, end_month, end_day))
        self.translation.search.append(search)
            
    def translate_database(self, args):
        """translate which database to use

        only support for ast and phy, bbb does not support arxiv value, classic does not support general
        no support to select multiple dbs
        """
        db = args.pop('db_key', None)
        filter = []
        classic_db_to_bbb = {'AST': 'astronomy', 'GEN': 'general', 'PHY': 'physics'}
        if db:
            bbb_db = classic_db_to_bbb.pop(db, None)
            if bbb_db:
                f = '{!type=aqp v=$fq_database}&fq_database=(' + 'database:"{}")'.format(bbb_db)
                self.translation.filter.append(urllib.quote(f))
            else:
                self.translation.warning_message.append('invalid database from classic {}'.format(db))
                print 'invalid database from classic {}'.format(db)

    def translate_results_subset(self, args):
        """subset/pagination currently not supported by bumblebee

        provide error message if pagination request is present"""
        number_to_return = args.pop('nr_to_return', None)
        start_nr = args.pop('start_nr', None)
        if number_to_return or start_nr:
            self.translation.error_message.append(urllib.quote('Result subset/pagination is not supported'))

    def translate_jou_pick(self, args):
        """translate for refereed, non-refereed"""
        jou_pick = args.pop('jou_pick', None)
        if jou_pick is None:
            # if not provided, include everything in results, which is default
            pass
        elif jou_pick == 'ALL':
            # include everything in results, which is default
            pass
        elif jou_pick == 'NO':
            # only include refereed journals
            self.translation.filter.append(urllib.quote('{!type=aqp v=$fq_property}&fq_property=(property:"refereed")'))
        elif jou_pick == 'EXCL':
            # only include non-refereed
            self.translation.filter.append(urllib.quote('{!type=aqp v=$fq_property}&fq_property=(property:"notrefereed")'))
        else:
            self.translation.error_message.append(urllib.quote('Invalid value for jou_pick: {}'.format(jou_pick)))

    def translate_return_req(self, args):
        """if return_req parameter is provided, it must be 'result' or None

        return error if any other value is supplied

        """
        return_req = args.pop('return_req', None)
        if return_req is None:
            pass
        elif return_req == 'result':
            pass
        else:
            self.translation.error_message.append(urllib.quote('Invalid value for return_req({}), should be "result"'.format(return_req)))

    def translate_property_filters(self, args):
        """filter query for property 

        several search fields translate to a Bumblebee filter query with property
        """
        to_bbb_property = {'article_sel': 'article', 'aut_note': 'note', 'data_link': 'data',
                           'open_link': 'OPENACCESS', 'preprint_link': 'eprint'}
        clauses = []
        for key in to_bbb_property.keys():
            if str(args.pop(key, None)).upper() == 'YES':
                value = to_bbb_property[key]
                self.translation.filter.append(urllib.quote('{{!type=aqp v=$fq_doctype}}&fq_doctype=(doctype:"{}")'.format(to_bbb_property.get(key))))

    def translate_qsearch(self, args):
        """translate qsearch parameter from single input form on classic_w_BBB_button.html

        return nonfielded metadata search query
        """
        qsearch = args.pop('qsearch', None)
        if qsearch:
            self.translation.search.append(qsearch + '&sort=' + urllib.quote('classic_factor desc, bibcode desc'))

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
        current_app.logger.info('Contacting vault/query ' + str(current_app.config['TESTING']))
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
