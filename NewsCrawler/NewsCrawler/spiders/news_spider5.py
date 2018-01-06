#-*-coding:utf-8 -*-
import scrapy
import requests
import json
from Sentiment.SentimentAnalyzer import SentimentAnalyzerSVM
import os
import pika
import re


class News1Spider(scrapy.Spider):
    name = 'news5'
    # seed url
    start_urls = [
        'http://news.163.com/17/1229/10/D6QM1MD1000187V9.html',  # 种子url
        'http://news.163.com/17/1229/00/D6PKNEUL0001875N.html',
        'http://money.163.com/17/1229/11/D6QQ9Q6F002580S6.html',
        'http://money.163.com/17/1229/07/D6QB5V0F0025816E.html'
    ]

    def parse(self, response):
        path = os.path.join(os.path.abspath('..'), 'News')
        # 预说明
        pagetoken = response.url.split('/')[-1].split('.')[0]  # url中标志页面的16位字符
        filename = response.url.split('/')[-4] + response.url.split('/')[-3] + '_' + pagetoken + '.txt'  # 文件名
        page_dic = {}  # 该字典存放整个页面的内容，最后转为json格式写入文件
        # --------------------------------页面url、题目、正文的抓取------------------------------------------#
        page_dic["news_id"] = pagetoken
        # 页面的url
        page_dic["url"] = response.url

        # 页面的题目
        page_dic["title"] = ""
        titles = response.xpath('//*[@id="epContentLeft"]/h1').extract()
        try:
            page_dic["title"] = titles[0].replace('"', '').replace(':', '').replace('<h1>', '').replace('</h1>', '')
        except:
            page_dic["title"] = "Passage without title"

        # 页面的评论数量
        page_dic["heat"] = ""  # 暂时记为空，后面用评论的条数作为热度

        # 页面的时间
        aa = response.xpath('//*[@id="epContentLeft"]/div[1]/text()').extract_first()
        time = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', aa)[0]
        page_dic["time"] = time

        # 页面的频道
        page_dic["channel"] = response.url.split('.')[0].split('/')[2]

        # 页面的正文
        page_dic["text"] = ""
        text = response.xpath('//*[@id="endText"]/p/text()').extract()
        for section in text:
            page_dic["text"] += section.replace("\n", "").replace('"', '').replace(':', '')

        # --------------------------------------------页面评论的抓取------------------------------------------#
        # 当前页面对应的评论页面的url
        comment_url = "http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/" + pagetoken + "/comments/hotList?callback=bowlder.cb._1&limit=10&showLevelThreshold=72&headLimit=1&tailLimit=2&offset=0&ibc=jssdk"

        # 请求评论页面, 使用requests代替urlopen
        mmheaders = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64…) Gecko/20100101 Firefox/57.0"
        }
        html = requests.get(comment_url).text
        html_json = html.split('(\n')[1].split(');')[0]
        # 将评论页面的json对象转化为字典，便于提取所需信息
        comment_dic = json.loads(html_json)

        # 页面的评论
        page_dic["comment"] = []

        # 特殊说明：定义了一个列表来存放当前页面的数条热评，
        # 列表中的每个元素为一个字典，对应一条评论
        # 字典（即一条评论）包括三个字段：创建时间、用户和内容

        # 逐条分析评论，每条评论包含三个要素：创建时间、用户和内容
        sas = SentimentAnalyzerSVM()
        for i in comment_dic["comments"]:
            a_comment = {"createTime": "", "username": "", "content": ""}  # 定义字典临时存放每条评论的：创建时间、用户、内容

            # --------------------本条评论的创建时间-------------------------#
            a_comment["createTime"] = comment_dic["comments"][i]["createTime"]

            # --------------------发起本条评论的用户-------------------------#
            try:
                a_comment["username"] = comment_dic["comments"][i]["user"]["nickname"]
            # print comment_dic["comments"][i]["user"]["nickname"]
            except:  # 有的评论没有nickname，有的包含特殊字符，均设为空
                print("no nickname")
                a_comment["username"] = ""

            # ----------------------本条评论的内容---------------------------#
            try:
                a_comment["content"] = comment_dic["comments"][i]["content"].replace("\n", "").replace('"', '').replace(
                    ':', '')
            except:  # 若该条评论中含有表情等特殊字符，则丢弃，记为空
                print("illegal charactor in content")
                a_comment["content"] = ""
                a_comment["emotion"] = "0"

            # 情感分析
            if a_comment["content"]:
                try:
                    a_comment["emotion"] = sas.analyze(a_comment['content'])
                    # a_comment["emotion"] = '0'
                except:
                    a_comment['emotion'] = '0'
            # 将这条评论加入到评论列表page_dic["comment"]中
            page_dic["comment"].append(a_comment)

        page_dic["heat"] = len(page_dic["comment"])

        # ----------------------------写入文件-------------------------------#

        # 将存放整个页面信息的字典page_dic转为json格式数据
        page_json = json.dumps(page_dic, ensure_ascii=False, indent=4)
        # 将json写入文件
        abs_name = path + '/' + filename
        with open(abs_name, 'at', encoding='utf-8') as f:
            f.write(page_json)
        # self.post_message(filename)

        # 用正则表达式匹配合适格式的网页url，继续请求
        next_pages = re.findall(r'http://[a-z]{1,7}.163.com/\d{2}/\d{4}/\d{2}/\w{16}.html',
                                response.body.decode('latin-1'))
        for next_page in next_pages:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def post_message(self, filename):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='127.0.0.1', port=5672))  # 定义连接池
        channel = connection.channel()
        # init the queue
        channel.queue_declare(queue='news')
        channel.exchange_declare(exchange='News', exchange_type='fanout', durable=True)
        channel.queue_bind(queue='news', exchange='News')
        # routing_key declare the queue name
        # The type of News Exchange is fanout, its like broadcat, posting the message to all its binding queues,
        # hence there is no need to bind routing_key
        channel.basic_publish(exchange='News', routing_key='1', body=filename)
        print('send success msg to rabbitmq')
        connection.close()
