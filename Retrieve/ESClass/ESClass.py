import json
import requests
from ESClass import ReadFile
from ESClass.GetDataSets import get_stopwords
import time
# elasticsearch path cannot contains the Chinese Characters, which makes the access denied error
class ESClass:
    def __init__(self, base_url):
        self.headers = {
            'json':{'Content-Type':'application/json'},
            'normal':{}
        }
        self.analyzer = {
            "ik_max":"ik_max_word",
            "ik_smart":"ik_smart",
            "news1":"news_analyzer",
            "news2":"standard"
        }
        self.index_name = 'test'
        self.type_name = 'news'
        self._base_url = base_url
        self.base_url = base_url + self.index_name + '/' + self.type_name + '/'
        print(self.base_url)
        # set your own file_folder
        self.file_folder = 'N:\\News'
        self.debug = True

    def response(self,message):
        print(message)
        return

    # first create index, do not create index and type at once
    def check_index_if_exists(self):
        r = requests.get(self._base_url + self.index_name)
        if r.status_code != 404:
            return True

    def create_index(self):
        index_name = self.index_name
        type_name = self.type_name
        index_url = self._base_url + index_name
        r = requests.get(index_url)
        #index already exists
        if r.status_code != 404:
            self.response("Index \""+ index_name + "\" already exists")
            return
        settings = \
            {
                "settings":{
                    "number_of_shards" :   1,
                    "number_of_replicas" : 0,
                    "analysis":{
                        "analyzer":{
                            "news_analyzer":{
                                "type":"ik_smart",
                                "stopwords_path":get_stopwords()
                            }
                        }
                    }
                },
                type_name: {
                    "properties": {
                        #news1 ik analyzer
                        #news2 standard analyzer
                        #suggest is actually a title copy to achieve auto complete
                        "news_id": {
                            "type": "text",
                            "index": "not_analyzed"
                        },
                        "title": {
                            "type": "text",
                            "analyzer": self.analyzer['news1'],
                            "search_analyzer": self.analyzer['news1'],
                        },
                        "title1":{
                            "type": "keyword",
                            "analyzer": self.analyzer['news2'],
                            "search_analyzer": self.analyzer['news2']
                        },
                        "tag":{
                            "type": "completion",
                            "preserve_separators" : 'false',
                            "preserve_position_increments" : 'false',
                            "analyzer": 'ik_max_word',
                            "search_analyzer": 'ik_max_word'
                        },
                        "text": {
                            "type": "text",
                            "analyzer": self.analyzer['news1'],
                            "search_analyzer": self.analyzer['news1'],
                        },
                        "text1": {
                            "type": "text",
                            "analyzer": self.analyzer['news2'],
                            "search_analyzer": self.analyzer['news2']
                        },
                        "url": {
                            "type": "text"
                        },
                        "heat":{
                            "type": "integer",
                            "index": "not_analyzed"
                        },
                        "date":{
                            "type": "date",
                            "format": "yyyy-MM-dd HH:mm:ss"
                        },
                        "timestamp": {
                            "type": "date"
                        },
                        "channel":{
                            "type": "text",
                            "index": "not_analyzed"
                        },
                        "comment": {
                            "type": "text",
                            "analyzer": self.analyzer['news1'],
                            "search_analyzer": self.analyzer['news1']
                        }
                    }
                }

            }
        settings_json = json.dumps(settings)
        r = requests.put(index_url, data = settings_json, headers = self.headers['json'])
        return r.text

    def suggest(self, query = None):
        suggest_url = self.base_url+ '_search?pretty=true'
        print(suggest_url)
        suggest_json = {
            "suggest":{
                "news-suggest": {
                    "text": query,
                    "phrase":{
                        "field": "title",
                        "highlight": {
                            "pre_tag": "<em>",
                            "post_tag": "</em>"
                        }
                    }
                }
            }
        }
        r = requests.post(suggest_url, data=json.dumps(suggest_json, ensure_ascii=False).encode('utf-8'), headers = self.headers['json'])
        return r.text

    #create new mapping using index/type/_mapping api to create mapping
    def create_mapping(self, mappings = {}):
        mapping_url = self.base_url + '_mapping'
        # http://www.jianshu.com/p/f169e70364d4
        if mappings:
            mapping_request = mappings
        else:
            return
        r = requests.put(mapping_url, data = json.dumps(mapping_request), headers = self.headers['json'])
        return r.text

    #不默认指明index，以免误删除
    def delete_index(self):
        index_url = self._base_url + self.index_name
        r = requests.delete(index_url, headers = self.headers['normal'])
        return r.text

    #batch delete
    def delete_data(self,  query={}):
        delete_url = self.base_url + '_delete_by_query?pretty=true'
        #if query is empty, delete all data
        if not query:
            query = {
                "query":{
                    "match_all":{

                    }
                }
            }
            query_request = json.dumps(query, ensure_ascii='False')
        else:
            query_request = json.dumps(query, ensure_ascii='False')
        r = requests.post(delete_url, data = query_request, headers = self.headers['json'])
        return r.text

    def insert_bulk_data(self, num):
        file_folder = self.file_folder
        bulk_url = self.base_url + '_bulk'
        # get bulk data -> ready to bulk insert
        for bulk_data in self.generate_bulk_insert_data(file_folder, num):
            r = requests.post(bulk_url, data = bulk_data.encode('utf-8'), headers = self.headers['json'])
            return r.content
            # 若为调试，只插入一批次
            #assert not self.debug

    def insert_crawled_data(self, filename):
        # crawled data is single file format
        # 1. copy the title and text
        # 2. change the comment content to json format text
        with open(filename, 'rt', encoding='utf-8') as f:
            json_raw_data = f.read()
        dict_data = json.loads(json_raw_data)
        dict_data['title1'] = dict_data['title']
        dict_data['text1'] = dict_data['text']
        dict_data['commentnumber'] = int(dict_data['commentnumber'])
        dict_data['comment'] = json.dumps(dict_data['comment'], ensure_ascii=False)
        dict_data['tag_suggest'] = {"input":dict_data['title']}

        json_data = json.dumps(dict_data, ensure_ascii=False)
        insert_url = self.base_url + dict_data['news_id']
        r = requests.post(insert_url, data = json_data.encode('utf-8'), headers = self.headers['json'])
        return r.content

    def generate_bulk_insert_data(self, file_folder, num):
        read_file = ReadFile.ReadFile(file_folder)
        # return list data -> generate bulk data
        # list data contains json like data
        # add action and meta data to every json data
        # 进行数据冗余
        # 从url指定位置，减少每次action动作的数据
        action = { "index":  {}}
        bulk_data = ""
        for data_list in read_file.get_data(num):
            # data list -> data
            # 传过来的data为从源文件取出的json格式
            # 对content做数据冗余，先将json载入为map，再添加，然后再dumps为json格式
            for data in data_list:
                try:
                    data_map = json.loads(data,encoding='utf-8')
                    data_map['title1'] = data_map['title']
                    data_map['tag'] = {"input": data_map['title']}
                    data_map['text1'] = data_map['text']
                    data_map['time'] = data_map['time']
                    data_map['timestamp'] = time.mktime(time.strptime(data_map['time'], '%Y-%m-%d %H:%M:%S'))
                    bulk_data += json.dumps(action, ensure_ascii=False) + '\n' + json.dumps(data_map, ensure_ascii=False) + '\n'
                except:
                    continue
            bulk_data += '\n'
            yield(bulk_data)
            bulk_data = ""

    def show_index(self):
        cat_url = self._base_url + '_cat/indices?v'
        r = requests.get(cat_url)
        return r.text

    def show_type(self):
        type_url = self._base_url + self.index_name + '/_search?pretty=true'
        r = requests.get(type_url)
        return r.text

    def get_hot_data(self, query):
        if not query:
            query_string = {
                "query": {
                    "match_all": {

                    },
                    'sort': {
                        'time': {
                            'order': 'desc'
                        }
                    }
                }
            }
        else:
            query_string = {
            'query':{
                'query_string':{
                    "fields":['text1','text','title','title1'],
                        "query": query,
                        "analyze_wildcard": "true",
                        'allow_leading_wildcard': "true"
                }
            },
            'sort':{
                'time': {
                    'order':'desc'
                }
            }
        }
        return requests.get(self.base_url + '_search?pretty=true', data = json.dumps(query_string, ensure_ascii=False).encode('utf-8'), headers=self.headers['json'])

    def get_related_data_right(self, input):
        return self.standard_search(input)

    def get_related_data_left(self, input):
        return self.standard_search(input)
    # generate query json and call matched search function
    # 1. query need to be json format
    # 2. query need to be encode 'utf-8' when requests.get
    def input_search(self, query, _size, _size_skip, _sort_type):
        sort_json = {
            "timestamp": "desc",
            "heat": "desc",
            "score": "desc"
        }
        if '?' in query or '*' in query:
            query_json = {
                "from":_size_skip, "size":_size,
                "query":{
                    "query_string":{
                        "fields":['text1','text','title','title1'],
                        "query": query,
                        "analyze_wildcard": "true",
                        'allow_leading_wildcard': "true"
                    }
                },
                "sort":{
                    _sort_type:{"order":"desc"}
                }
            }
            return self.standard_search(query = json.dumps(query_json, ensure_ascii=False).encode('utf-8'))
        if '/and/' in query:
            query_split = query.split('/and/')
            query_split_wrapper = [{"match": {"desc": x}} for x in query_split]
            query_json = {
                "from": _size_skip, "size": _size,
                "query":{
                    "bool":{
                        "must": query_split_wrapper
                    }
                },
                "sort": {
                    _sort_type: {"order": "desc"}
                }
            }
            return self.standard_search(query = json.dumps(query_json, ensure_ascii=False).encode('utf-8'))
        else:
            query_json = {
                "from": _size_skip, "size": _size,
                "query":{
                    "query_string":{
                        "fields":['title'],
                        "query": query,
                        "analyze_wildcard": "true",
                        'allow_leading_wildcard': "true"
                    }
                },
                "sort": {
                    _sort_type: {"order": "desc"}
                }
            }
            print(query_json)
            return self.standard_search(query = json.dumps(query_json, ensure_ascii=False).encode('utf-8'))

    def wildcard_search(self,  query = None):
        search_url = self.base_url + '_search?pretty=true'
        r = requests.get(search_url, data = query, headers = self.headers['json'])
        self.response(r.text)

    def standard_search(self,  query = None):
        # query is json,
        search_url = self.base_url +'_search?pretty=true'
        if query:
            r = requests.get(search_url, data = query, headers = self.headers['json'])
        else:
            r = requests.get(search_url, headers = self.headers['normal'])
        return r.text

    #test function
    def search_test(self, query = {}):
        search_url = self.base_url + '_search'
        #Decide which header depend on query
        if query:
            headers = self.headers['normal']
        else:
            headers = self.headers['json']
        r = requests.get(search_url, data = query, headers = headers)
        return r.text
    #test ik_analyzer token result by inputing a constant text
    def analyzed_test(self):
        analyzed_url = self._base_url + '_analyze'

        analyze_request_raw = {
            "analyzer": 'chinese',
            "text": "中国科学院大学是世界上最好的大学"
        }
        analyze_request_data = json.dumps(analyze_request_raw, ensure_ascii=False)
        r = requests.get(analyzed_url, data = analyze_request_data.encode('utf-8'), headers = self.headers['json'])
        print(r.text)

    def get_by_news_id(self, news_id):
        query_json = {
            "query": {
                "query_string":{
                    "fields":['news_id'],
                    "query": news_id,
                    "analyze_wildcard": "true",
                    'allow_leading_wildcard': "true"
                }
            }
        }
        query_news = self.map2json(query_json)
        news_content = self.standard_search(query=query_news)
        return news_content

    def map2json(self, map):
        return json.dumps(map, ensure_ascii=False).encode('utf-8')

    def restart(self):
        self.delete_index()
        self.create_index()
        self.insert_bulk_data(1)