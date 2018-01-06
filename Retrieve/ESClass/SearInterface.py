from ESClass.ESClass import ESClass
import json
class Search():
    def __init__(self):
        self.es = ESClass('http://localhost:9200/')

    def map2json(self, map):
        return json.dumps(map, ensure_ascii=False).encode('utf-8')

    def show_hot(self, num):
        query = {
            "size": int(num),
            "query": {
                "match_all": {}
            },
            "sort": {"timestamp": {"order": "desc"},
                     "heat": {"order": "desc"}}
        }
        return self.es.standard_search(query = self.map2json(query))

    def input_search(self, query='', size=10, size_skip=0, sort_type='_score'):
        list1 = self.es.input_search(query=query,_size_skip=size_skip, _size=size, _sort_type = sort_type)
        tmp_map = json.loads(list1)
        list2 = self.es.input_search(query = tmp_map['hits']['hits'][0]['_source']['title'],_size_skip=size_skip, _size=size, _sort_type = sort_type)
        return list1, list2
    def get_news_by_id(self, news_id):
        result = self.es.get_by_news_id(news_id=news_id)
        return result