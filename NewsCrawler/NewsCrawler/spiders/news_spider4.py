#-*-coding:utf-8 -*-
import scrapy
import requests
import json
from Sentiment.SentimentAnalyzer import SentimentAnalyzerSVM
import os
import pika
import re


class News1Spider(scrapy.Spider):
    name = 'news4'
    # seed url
    start_urls = [
        'http://news.163.com/17/1229/10/D6QM0D7N0001875P.html',
        'http://news.163.com/17/1229/11/D6QPCIQR0001899N.html',
        'http://news.163.com/17/1229/11/D6QQNMIP000187VE.html',
        'http://news.163.com/17/1229/11/D6QPC4CN00018AOQ.html'
    ]

    def parse(self, response):
        path = os.path.join(os.path.abspath('..'),'News')
        pagetoken = response.url.split('/')[-1].split('.')[0]
        filename = response.url.split('/')[-4] + response.url.split('/')[-3] + '_' + pagetoken + '.txt'
        page_dic = {}
        page_dic["news_id"] = pagetoken
        page_dic["url"] = response.url

        page_dic["title"] = ""
        titles = response.xpath('//*[@id="epContentLeft"]/h1').extract()
        try:
            page_dic["title"] = titles[0].replace('"', '').replace(':', '').replace('<h1>', '').replace('</h1>', '')
        except:
            page_dic["title"] = "Passage without title"

        page_dic["heat"] = ""

        aa = response.xpath('//*[@id="epContentLeft"]/div[1]/text()').extract_first()
        time = re.findall(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', aa)[0]
        page_dic["time"] = time

        page_dic["channel"] = response.url.split('.')[0].split('/')[2]

        page_dic["text"] = ""
        text = response.xpath('//*[@id="endText"]/p/text()').extract()
        for section in text:
            page_dic["text"] += section.replace("\n", "").replace('"', '').replace(':', '')

        comment_url = "http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/" + pagetoken + "/comments/hotList?callback=bowlder.cb._1&limit=10&showLevelThreshold=72&headLimit=1&tailLimit=2&offset=0&ibc=jssdk"

        mmheaders = {
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate, br",
            "Accept-Language":"en-US,en",
            "Connection":"keep-alive",
            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64…) Gecko/20100101 Firefox/57.0"
        }
        html = requests.get(comment_url).text
        html_json = html.split('(\n')[1].split(');')[0]
        comment_dic = json.loads(html_json)

        page_dic["comment"] = []

        sas = SentimentAnalyzerSVM()
        for i in comment_dic["comments"]:
            a_comment = {"createTime": "", "username": "", "content": ""}

            a_comment["createTime"] = comment_dic["comments"][i]["createTime"]

            try:
                a_comment["username"] = comment_dic["comments"][i]["user"]["nickname"]
            except :
                print("no nickname")
                a_comment["username"] = ""

            try:
                a_comment["content"] = comment_dic["comments"][i]["content"].replace("\n", "").replace('"', '').replace(
                    ':', '')
            except:
                print("illegal charactor in content")
                a_comment["content"] = ""
                a_comment["emotion"] = "0"

            if a_comment["content"]:
                try:
                    a_comment["emotion"] = '0'
                    #a_comment["emotion"] = sas.analyze(a_comment['content'])
                except:
                    a_comment['emotion'] = '0'
            page_dic["comment"].append(a_comment)

        page_dic["heat"] = len(page_dic["comment"])

        page_json = json.dumps(page_dic, ensure_ascii = False, indent = 4)
        abs_name = path+'/'+filename
        with open(abs_name, 'at', encoding='utf-8') as f:
            f.write(page_json)
        next_pages = re.findall(r'http://[a-z]{1,7}.163.com/\d{2}/\d{4}/\d{2}/\w{16}.html', response.body.decode('latin-1'))
        for next_page in next_pages:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

    def post_message(self, filename):
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='127.0.0.1', port=5672))
        channel = connection.channel()
        #init the queue
        channel.queue_declare(queue='news')
        channel.exchange_declare(exchange='News', exchange_type='fanout',durable=True)
        channel.queue_bind(queue='news', exchange='News')
        # routing_key declare the queue name
        # The type of News Exchange is fanout, its like broadcat, posting the message to all its binding queues,
        # hence there is no need to bind routing_key
        channel.basic_publish(exchange='News', routing_key='1',body=filename)
        print('send success msg to rabbitmq')
        connection.close()
