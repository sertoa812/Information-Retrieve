#-*- coding: utf-8 -*-

import re
import scrapy
path = r'D:\Experiment\IR_Scrapy\Neteasenews\result\\'              #爬取结果存放路径

class NeteaseSpider(scrapy.Spider):
    name = "netease1"                                               #爬虫的名字
    start_urls = [
        'http://news.163.com/17/1126/01/D44NK8R1000187VI_mobile.html',     #种子url
		'http://news.163.com/17/1126/01/D44NK8QJ000187VI.html',
		'http://news.163.com/17/1126/01/D44MP65P00018AOQ.html',
		'http://news.163.com/17/1126/00/D44M826A0001899N.html'
    ]

    #网页的html源码交给parse函数去解析
    def parse(self, response):
	
		#txt文档命名
		filename = response.url.split('/')[-4] + response.url.split('/')[-3] + '_' + response.url.split('/')[-2] + '_' + response.url.split('/')[-1].split('.')[0] + '.txt'                      
		
		#针对mobile端进行优化
		#将页面url写入文档
		f = open(path + filename, 'wb')
		f.write(response.url + '\n')                         
		
		#将新闻标题写入文档
		titles = response.xpath('//h1').extract()       
		for segment in titles:
			f.write(segment.encode('utf-8') + '\n')
		
		#将新闻正文写入文档
		text = response.xpath('/article//p/text()').extract()
		for section in text:
			f.write(section.encode('utf-8') + '\n')
		
		#爬取评论
		f.write('\n\n'+'comment:'+'\n')
		pinglun = response.xpath('/ul[@class="commentbox-wrap"]//p[@class="cmomment-content"]').extract()
		for item in pinglun:
			f.write(item.encode('utf-8') + '\n')
		f.close()
		
		#用正则表达式匹配合适格式的网页url，继续请求
		next_pages = re.findall(r'http://[a-z]{1,7}.163.com/\d{2}/\d{4}/\d{2}/\w{16}.html',response.body)
		for next_page in next_pages:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(next_page, callback=self.parse)