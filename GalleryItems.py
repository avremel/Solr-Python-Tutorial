import simplejson
from .ProcessSolrResponse import ProcessSolrResponse
from .QuerySolr import QuerySolr

class GalleryItems:

    def __init__(self, current_filter):

        # current_filter contains: current_brand, current_collection, current_sub_collection, sorting, facet_filter, page, per_page, query_string, facets_clicked
        for k, v in current_filter.items():
            setattr(self, k, v)

        self.solr_url = 'http://localhost:<port>/solr/<core/select?'
        self.in_stock = 'in_stock:true'
        self.sort_options = {
            'low': 'price asc, title asc',
            'high': 'price desc, title asc',
            'alpha': 'title asc'
        }
        self.fields_returned = 'title,price,barcode,image'
        self.facet_fields = [
            'gender', 
            'style', 
            'material', 
        ]
        self.price_ranges = [
            '[*,500)', 
            '[500,1000)', 
            '[1000,2500)', 
            '[5000,7500)', 
            '[5000,7500)', 
            '[7500,*]'
        ]
        self.generic_args = [
            ('facet', 'on'),
            ('facet.limit', '-1'),
            ('facet.mincount', '1'),
            ('defType', 'edismax'),
            ('qf', 'copyall copyallphonetic'),
            ('tie', '1.0'),
            ('wt', 'json'),
        ]
        self.filters = []
        self.solr_args = []
        query_solr = QuerySolr(self.solr_args, self.solr_url).response
        self.raw_response = query_solr['raw_response']
        self.complete_url = query_solr['complete_url']

        self.setup_query()
        self.process_response()


    def setup_query(self):
        self.apply_per_page()
        self.apply_start_row()
        self.apply_query_string()
        self.apply_facet_filters()
        self.apply_brand_filter()
        self.apply_collection_filter()
        self.apply_sub_collection_filter()
        self.apply_in_stock_filter()
        self.apply_sorting()
        self.apply_fields_returned()
        self.apply_facet_fields()
        self.apply_facet_pivots()
        self.apply_price_ranges()
        self.apply_generic_args()
    
    def process_response(self):
        # seperated response processing into new class
        self.raw_response = ProcessSolrResponse({
            'raw_response': self.raw_response,
            'facet_filter': self.facet_filter,
            'current_collection': self.current_collection,
            'current_sub_collection': self.current_sub_collection
        }).raw_response

    def apply_per_page(self):
        self.solr_args.append(('rows', self.per_page))

    def apply_start_row(self):
        # calculate offset for pagination
        start_row = str(int(self.page) * int(self.per_page))
        self.solr_args.append(('start', start_row))
    
    def apply_query_string(self):
        query_string = ''

        if self.query_string:
            query_string = self.query_string
        else:
            query_string = "*:*"

        self.solr_args.append(('q', query_string))

    def there_are_facets(self):
        there_are_facets = False
        for facet, facet_arr in self.facet_filter.items():
            if len(facet_arr) > 0:
                there_are_facets = True
        return there_are_facets

    def apply_facet_filters(self):
        if self.there_are_facets():
            for facet, facet_arr in self.facet_filter.items():
                if len(facet_arr) > 0:
                    new_facet_arr = []
                    for a_facet in facet_arr:
                        if facet == 'price_range':
                            # replacet facet.interval syntax with range query syntax
                            formatted_a_facet = str(a_facet).replace(')', '}').replace(',', ' TO ')
                            new_facet_arr.append("{0}: {1}".format(facet, formatted_a_facet))
                        else:
                            new_facet_arr.append("{0}: \"{1}\"".format(facet, a_facet))
                    if facet in self.facets_clicked:
                        # apply tagging for multi-select
                        self.solr_args.append(('fq', "{!tag=" + facet + "}" + ' OR '.join(new_facet_arr)))
                    else:
                        self.solr_args.append(('fq', ' OR '.join(new_facet_arr)))

    def apply_brand_filter(self):
        if self.current_brand:
            self.solr_args.append(('fq', "brand: \"{0}\"".format(self.current_brand)))

    def apply_collection_filter(self):
        if self.current_collection:
            collection_arr = []
            for s in self.current_collection:
                collection_arr.append("collection: \"{0}\"".format(s))
            # apply tagging for multi-select
            self.solr_args.append(('fq', "{!tag=brand_tree}" + ' OR '.join(collection_arr)))

    def apply_sub_collection_filter(self):
        if self.current_sub_collection:
            ss_arr = []
            for ss in self.current_sub_collection:
                ss_arr.append("sub_collection: \"{0}\"".format(ss['value']))
            # apply tagging for multi-select
            self.solr_args.append(('fq', "{!tag=brand_tree}" + ' OR '.join(ss_arr)))

    def apply_in_stock_filter(self):
        self.solr_args.append(('fq', self.in_stock))

    def apply_sorting(self):
        # defaults to relevance scoring
        if self.sorting in self.sort_options:
            sort = self.sort_options[self.sorting]
            self.solr_args.append(('sort', sort))

    def apply_fields_returned(self):
        self.solr_args.append(('fl', self.fields_returned))

    def apply_facet_fields(self):
        # for simplicity, price range is considered a facet field 
        for facet in self.facet_fields:
            if facet in self.facets_clicked:
                # apply exclude for multi-select
                if facet == 'price_range':
                    self.solr_args.append(('facet.interval', "{!ex=" + facet + "}" + facet))
                else:
                    self.solr_args.append(('facet.field', "{!ex=" + facet + "}" + facet))
            else:
                if facet == 'price_range':
                    self.solr_args.append(('facet.interval', facet))
                else:
                    self.solr_args.append(('facet.field', facet))

    def apply_facet_pivots(self):
        if self.current_collection or self.current_sub_collection:
            # apply exclude for multi-select
            self.solr_args.append(('facet.pivot', '{!ex=brand_tree}brand,collection,sub_collection'))
        else:
            self.solr_args.append(('facet.pivot', 'brand,collection,sub_collection'))

    def apply_price_ranges(self):
        for range in self.price_ranges:
            self.solr_args.append(('facet.interval.set', range))

    def apply_generic_args(self):
        self.solr_args = self.solr_args + self.generic_args
        