# SolrPython
Example implementation for [my tutorial](https://dev.to/avremel/solr--pythona-tutorial-3cni) over at [dev.to](https://dev.to/).

The code here is quite involved, as it implements `facet.pivot's`, price ranges with `facet.interval`, multi-select with tagging and excluding.

Here are my questions on StackOverflow for more context:
* [Multi-select](https://stackoverflow.com/questions/49987748/solr-gallery-page-with-multi-select)
* [`facet.mincount` won't help for `facet.interval`](https://stackoverflow.com/questions/50026135/facet-mincount-ignored-in-range-faceting). Not a big deal as you can control that in the front-end.
* [`facet.pivot.mincount` crashes server](https://stackoverflow.com/questions/49837742/solr-facet-pivot-mincount-0-crashes-server)
* [Some direction on phrase based search](https://stackoverflow.com/questions/49806344/solr-nested-edismax-query)
