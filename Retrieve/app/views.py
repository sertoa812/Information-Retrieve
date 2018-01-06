from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from ESClass import ESClass
from ESClass.SearInterface import Search
import json
import random
# Create your views here.
def control(request):
    search = Search()
    js = json.loads(search.show_hot(24))
    hot = {}
    source = js['hits']['hits']
    for i in range(len(source)):
        hot[source[i]['_source']['title']] = source[i]['_source']['url']
        #print(source[i]['_source']['url'])
    return HttpResponse(str(hot))
    #return JsonResponse(json, safe=False)

def home(request):
    if request.is_ajax():
        flag = request.GET['fresh']
        if flag == 'fresh':
            search = Search()
            js = json.loads(search.show_hot(100))
            hot = {}
            source = js['hits']['hits']
            list = range(0, 100)
            sam_index = random.sample(list, 6)
            for i in range(6):
                hot[source[sam_index[i]]['_source']['title']] = source[sam_index[i]]['_source']['url']
            freshDict = {'教育部否认考研数学泄题:视频例题与实考试题不同': 'http://dy.163.com/v2/article/detail/D6JQOIR4051485CG.html',
                         '新华社长篇述评告诉你习近平如何领航中国经济': 'http://news.163.com/17/1226/09/D6ISFN08000189FH.html',
                         '坎特力压姆巴佩当选2017法国足球先生 本泽马第三': 'http://sports.163.com/17/1226/18/D6JRQIFQ00058781.html',
                         '经纪公司惨遭打脸！网曝邹市明出场费仅5500美金': 'http://ent.163.com/17/1226/14/D6JCUMOB00038FO9.html',
                         '人民币强势升值:一天升破4个关口 创3个月来新高': 'http://money.163.com/17/1225/19/D6HD08GF002580S6.html',
                         '北京三环现单价低于6万的学区房 超8成二手房降价': 'http://money.163.com/17/1226/07/D6ILSL8A002580SJ.html'}
            return JsonResponse(hot)
            #return HttpResponse('1')

def index(request):
    newsDict = {'国产大飞机"三兄弟"蓝天聚首 开启航空强国新时代': 'http://news.163.com/17/1225/13/D6GMBRUL000189FH.html',
                '北京证监局:责令贾跃亭2017年12月31日前回国履责': 'http://news.163.com/17/1225/21/D6HJ8QDB0001899O.html',
                '朝鲜称安理会最新制裁是"战争行为" 外交部回应': 'http://news.163.com/17/1225/18/D6H730LA0001899N.html',
                '英媒评英超半程最佳:埃及梅西入选 曼城8-1曼联': 'http://sports.163.com/17/1225/18/D6H8627B00058781.html',
                '皇马"高考倒计时"还剩50天 欧冠出局=万劫不复': 'http://sports.163.com/17/1225/22/D6HLA78800058781.html',
                '陈冠希二姐晒全家福 秦舒培搂女儿满脸幸福': 'http://ent.163.com/17/1225/18/D6H7PO7300038FO9.html'}
    search = Search()
    js = json.loads(search.show_hot(6))
    hot = {}
    source = js['hits']['hits']
    for i in range(len(source)):
        hot[source[i]['_source']['title']] = source[i]['_source']['url']
    return render(request, "index1.html", {'newsDict': hot})

def complete(request):
    search = request.GET['search']
    if search is not None:
        completeList = ['尤文图斯',
                        '切尔西',
                        '巴塞罗那',
                        '山东鲁能',
                        '国安傻逼']
        return JsonResponse(completeList, safe=False)

def search(request):
    if request.method == 'POST':
        cont = request.POST['content']
        skip = 1
    if request.method == 'GET':
        cont = request.GET['content']
        skip = request.GET['skip']
    se = Search()
    print(cont)
    list1, list2 = se.input_search(query=cont, size_skip=(int(skip)-1)*10)
    js1 = json.loads(list1)
    js2 = json.loads(list2)
    #dic1 = {}
    #dic2 = {}
    dic1 = []
    dic2 = []
    top1_rank = {}
    source1 = js1['hits']['hits']
    source2 = js2['hits']['hits']
    top1_rank['title'] = source1[0]['_source']['title']
    top1_rank['url'] = source1[0]['_source']['url']
    top1_rank['news_id'] = source1[0]['_source']['news_id']
    '''
    for i in range(1, len(source1)):
        dic1[source1[i]['_source']['title']] = source1[i]['_source']['url']

    for i in range(7):
        dic2[source2[i]['_source']['title']] = source2[i]['_source']['url']
     '''
    for i in range(1, len(source1)):
        dic = {}
        dic['title'] = source1[i]['_source']['title']
        dic['url'] = source1[i]['_source']['url']
        dic['summary'] = source1[i]['_source']['text'][0:150]
        dic['content'] = source1[i]['_source']['text']
        dic['news_id'] = source1[i]['_source']['news_id']
        dic1.append(dic)

    self_map = {
    'tech': '网易科技',
    'sports': '网易体育',
    'news': '网易新闻',
    'mobile': '网易移动',
    'ent': '网易娱乐',
    }

    for i in range(1, 8):
        dic = {}
        dic['title'] = source2[i]['_source']['title']
        dic['url'] = source2[i]['_source']['url']
        dic['channel'] = self_map[source2[i]['_source']['channel']]
        dic['time'] = source2[i]['_source']['time']
        dic2.append(dic)
    list3 = [i for i in range(1, 11)]

    return render(request, 'index2.html', {'top1_rank': top1_rank, 'dic1': dic1, 'dic2': dic2, 'search': cont, 'list3': list3})
    #return HttpResponse(str(dic1))
    #return render(request, 'index2.html', {'search': search, 'search1': '555'})
        #return HttpResponse(a)

def rank(request):
    if request.method == 'POST':
        cont = request.POST['original']
        keywords = request.POST['key']
        skip = 1
    if request.method == 'GET':
        cont = request.GET['original']
        keywords = request.GET['key']
        skip = request.GET['skip']
    se = Search()
    list1, list2 = se.input_search(query=cont, sort_type = keywords, size_skip=(int(skip)-1)*10)
    js1 = json.loads(list1)
    js2 = json.loads(list2)
    #dic1 = {}
    #dic2 = {}
    dic1 = []
    dic2 = []
    top1_rank = {}
    source1 = js1['hits']['hits']
    source2 = js2['hits']['hits']
    top1_rank['title'] = source1[0]['_source']['title']
    top1_rank['url'] = source1[0]['_source']['url']
    top1_rank['news_id'] = source1[0]['_source']['url']
    '''
    for i in range(1, len(source1)):
        dic1[source1[i]['_source']['title']] = source1[i]['_source']['url']

    for i in range(7):
        dic2[source2[i]['_source']['title']] = source2[i]['_source']['url']
     '''
    for i in range(1, len(source1)):
        dic = {}
        dic['title'] = source1[i]['_source']['title']
        dic['url'] = source1[i]['_source']['url']
        dic['summary'] = source1[i]['_source']['text'][0:150]
        dic['content'] = source1[i]['_source']['text']
        dic['news_id'] = source1[i]['_source']['news_id']
        dic1.append(dic)

    self_map = {
    'tech': '网易科技',
    'sports': '网易体育',
    'news': '网易新闻',
    'mobile': '网易移动',
    'ent': '网易娱乐',
    'money': '网易财经',
    }

    for i in range(1, 8):
        dic = {}
        dic['title'] = source2[i]['_source']['title']
        dic['url'] = source2[i]['_source']['url']
        dic['channel'] = self_map[source2[i]['_source']['channel']]
        dic['time'] = source2[i]['_source']['time']
        dic2.append(dic)
    list3 = [i for i in range(1, 11)]

    return render(request, 'index2.html', {'top1_rank': top1_rank, 'dic1': dic1, 'dic2': dic2, 'search': cont, 'list3': list3})
    #return render(request, 'index2.html')

def index2(request):
    if request.method == 'GET':
        news_id = request.GET['news_id']
        es = Search()
        result = es.get_news_by_id(news_id)
        js = json.loads(result)
        dic = {}
        source = js['hits']['hits'][0]['_source']
        dic['title'] = source['title']
        dic['url'] = source['url']
        dic['content'] = source['text']
        dic['comment'] = source['comment']
        mat = [0, 0, 1, 0, 0, 1, 0, 0, 0, 1]
        for item in dic['comment']:
            item['emotion'] = ''
            emo = random.randint(0, 9)
            if mat[emo] == 0:
                item['emotion'] = 'negative'
            else:
                item['emotion'] = 'positive'
    #return HttpResponse(str(dic))
    return render(request, "index3.html", {'dic': dic})


def suggest(request):
    if request.method == 'GET':
        keyword = request.GET['keyword']
        se = Search()
        raw_json, _ = se.input_search(query=keyword)
        tmp_result = json.loads(raw_json)
        result_list = tmp_result['hits']['hits']
        items = []
        for index, item in enumerate(result_list):
            if index == 6:
                break
            single_data = {'title':item['_source']['title']}
            items.append(single_data)
        suggests = json.dumps(items)
        print(suggests)
    return HttpResponse(suggests)