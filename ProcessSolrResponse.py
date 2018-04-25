import more_itertools as mit

class ProcessSolrResponse:

    def __init__(self, params):
        # params contains: raw_response, facet_filter, current_collection, current_sub_collection
        for k, v in params.items():
            setattr(self, k, v)
        
        self.collection_in_response = []
        self.sub_collection_in_response = []

        self.format_facet_field_response()
        self.include_price_ranges_in_facet_field_response()
        self.update_facet_filter_to_reflect_response()
        self.collection_and_sub_collection_in_response()
        self.update_collection_filter_to_reflect_response()
        self.update_sub_collection_filter_to_reflect_response()

    def format_facet_field_response(self):
        facets = {}
        for k,v in self.raw_response['facet_counts']['facet_fields'].items():
            facet_list = [list(facet) for facet in mit.chunked(v, 2)]
            facet_dict = {}
            for facet in facet_list:
                facet_dict[facet[0]] = facet[1]
            facets[k] = facet_dict

        self.raw_response['facet_counts']['facet_fields'] = facets

    def include_price_ranges_in_facet_field_response(self):
        # since price ranges are treated like a facet, inject into facet data
        self.raw_response['facet_counts']['facet_fields']['price_range'] = self.raw_response['facet_counts']['facet_intervals']['price_range']

    def update_facet_filter_to_reflect_response(self):
        # if facets in response don't include a facet the user clicked on, remove it
        # this ensures a fluid multi-select experience
        for facet, facet_arr in self.facet_filter.items():
            for a_facet in facet_arr:
                for key,value in self.raw_response['facet_counts']['facet_fields'].items():
                    if key == facet and a_facet not in [*value]:
                        self.facet_filter[facet].remove(a_facet)

    def collection_and_sub_collection_in_response(self):
        # track which collections or sub_collections facet.pivots were returned, to we can update user filter 
        # in update_collection_filter_to_reflect_response() and update_sub_collection_filter_to_reflect_response()
        for brand in self.raw_response['facet_counts']['facet_pivot']['brand,collection,sub_collection']:
            if 'pivot' in brand:
                for collection in brand['pivot']:
                    self.collection_in_response.append(collection['value'])
                    if 'pivot' in collection:
                        for sub_collection in collection['pivot']:
                            self.sub_collection_in_response.append(sub_collection['value'])

    def update_collection_filter_to_reflect_response(self):
        # update current collection selection to reflect what filter is showing. drop sub_collection if collection is dropped
        if self.current_collection:
            for collection in self.current_collection:
                if collection not in self.collection_in_response:
                    self.current_collection.remove(collection)
                    for ss in self.current_sub_collection:
                        if ss['parent'] == collection:
                            self.current_sub_collection.remove(ss)

    def update_sub_collection_filter_to_reflect_response(self):
        # update current sub_collection selection to reflect what filter is showing. drop sub_collection if collection is dropped
        if self.current_sub_collection:
            for ss in self.current_sub_collection:
                if ss['value'] not in self.sub_collection_in_response:
                    self.current_sub_collection.remove(ss)

