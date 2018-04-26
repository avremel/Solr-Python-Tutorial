from urllib.request import urlopen
import urllib.parse
import simplejson

class QuerySolr:

    def __init__(self, solr_args, solr_url):
        self.solr_url = solr_url
        self.solr_args = solr_args
        self.complete_url = ''
        self.response = {}
        self.create_url()
        self.query_solr()
        self.format_response()

    def create_url(self):
        encoded_query = urllib.parse.urlencode(self.solr_args)
        self.complete_url = self.solr_url + encoded_query

    def query_solr(self):
        connection = urlopen(self.complete_url)
        self.raw_response = simplejson.load(connection)

    def format_response(self):
        self.response = {'raw_response': self.raw_response, 'complete_url': self.complete_url}