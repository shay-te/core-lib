import pysolr


class SolrClient(object):

    __instance = None

    def __init__(self, solr_address):
        self.solr_client = pysolr.Solr(solr_address, always_commit=True)

    @staticmethod
    def init(solr_address):
        if SolrClient.__instance is None:
            SolrClient.__instance = SolrClient(solr_address)

    @staticmethod
    def solr():
        if SolrClient.__instance is None:
            raise NameError('SolrClient not initialized')
        return SolrClient.__instance.solr_client
