import scrapy
import requests
import json
from Sentiment.SentimentAnalyzer import SentimentAnalyzerSVM
import os
class News1Spider(scrapy.Spider):
    name = 'news2'
    #seed url
    start_urls = [
        'http://comment.news.163.com/news2_bbs/D5L8C4OF0001899N.html'
    ]

    def parse(self, response):
        text = response.text
        
        with open('./result/random', 'at', encoding='utf-8') as f:
            f.write(text)

        # 用正则表达式匹配合适格式的网页url，继续请求
        '''next_pages = re.findall(r'http://[a-z]{1,7}.163.com/\d{2}/\d{4}/\d{2}/\w{16}.html', response.body)
        for next_page in next_pages:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)'''
