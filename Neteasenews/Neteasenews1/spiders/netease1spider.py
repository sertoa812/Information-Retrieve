# -*- coding: utf-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import re
import scrapy
import urllib
import json
path = './result/'             #爬取结果存放路径

class NeteaseSpider(scrapy.Spider):
	name = "netease1"                                               #爬虫的名字
	start_urls = [
		'http://news.163.com/17/1214/17/D5KRAV1M000189FH.html',     #种子url
		'http://news.163.com/17/1215/02/D5LP25BI0001875P.html',
		'http://news.163.com/17/1215/00/D5LGOT500001875N.html',
		'http://news.163.com/17/1214/21/D5L8C4OF0001899N.html'
	]

	#网页的html源码交给parse函数去解析
	def parse(self, response):
	
		#预说明
		pagetoken = response.url.split('/')[-1].split('.')[0]       #url中标志页面的16位字符
		filename = response.url.split('/')[-4] + response.url.split('/')[-3] + '_' + pagetoken + '.txt'     #文件名
		page_dic = {}                                               #该字典存放整个页面的内容，最后转为json格式写入文件

		
		#--------------------------------页面url、题目、正文的抓取------------------------------------------#
		#页面的url
		page_dic["url"] = response.url		

		
		#页面的题目
		page_dic["title"] = ""
		titles = response.xpath('//*[@id="epContentLeft"]/h1').extract()
		try:
			page_dic["title"] = titles[0].replace('"', '').replace(':', '').replace('<h1>', '').replace('</h1>', '')
		except:
			page_dic["title"] = "Passage without title"
		
		
		#页面的正文
		page_dic["text"] = ""
		text = response.xpath('//*[@id="endText"]/p/text()').extract()
		for section in text:
			page_dic["text"] += section.replace("\n", "").replace('"', '').replace(':', '')
			#f.write(section.encode('utf-8') + '\n')
		
		
		#--------------------------------------------页面评论的抓取------------------------------------------#
		#当前页面对应的评论页面的url
		comment_url = "http://sdk.comment.163.com/api/v1/products/a2869674571f77b5a0867c3d71db5856/threads/" + pagetoken + "/comments/hotList?callback=bowlder.cb._1&limit=10&showLevelThreshold=72&headLimit=1&tailLimit=2&offset=0&ibc=jssdk"
		
		#请求评论页面
		html = urllib.urlopen(comment_url).read()
		html_json = html.split('(\n')[1].split(');')[0]
		#将评论页面的json对象转化为字典，便于提取所需信息
		comment_dic = json.loads(html_json)                    
		
		
		#页面的评论
		page_dic["comment"] = []
		
		#特殊说明：定义了一个列表来存放当前页面的数条热评，
		#列表中的每个元素为一个字典，对应一条评论
		#字典（即一条评论）包括三个字段：创建时间、用户和内容
		
		#逐条分析评论，每条评论包含三个要素：创建时间、用户和内容
		for i in comment_dic["comments"]: 
		
			a_comment = {"createTime":"", "username":"", "content":""}      #定义字典临时存放每条评论的：创建时间、用户、内容
			
			#--------------------本条评论的创建时间-------------------------#
			a_comment["createTime"] = comment_dic["comments"][i]["createTime"]
			
			
			#--------------------发起本条评论的用户-------------------------#
			try:
				a_comment["username"] = comment_dic["comments"][i]["user"]["nickname"]
				#print comment_dic["comments"][i]["user"]["nickname"]
			except KeyError:                                                #有的评论没有nickname，记为空
				print "no nickname"
				a_comment["username"] = ""
			except UnicodeEncodeError:                                      #若nickname中有特殊字符，记为空
				print "illegal charactor in nickname"
				a_comment["username"] = ""
				
			#----------------------本条评论的内容---------------------------#
			try:
				a_comment["content"] = comment_dic["comments"][i]["content"].replace("\n", "").replace('"', '').replace(':', '')
				#print comment_dic["comments"][i]["content"]
			except UnicodeEncodeError:                                    #若该条评论中含有表情等特殊字符，则丢弃，记为空
				print "illegal charactor in content"
				a_comment["content"] = ""
			
			#将这条评论加入到评论列表page_dic["comment"]中
			page_dic["comment"].append(a_comment)

		

		#----------------------------写入文件-------------------------------#
		#将存放整个页面信息的字典page_dic转为json格式数据
		page_json = json.dumps(page_dic, sort_keys=True, indent=4, separators=(',', ': '))
		#将json写入文件
		f = open(path + filename, 'wb')
		f.write(page_json.decode('unicode-escape'))
		f.close()
		
		
		#用正则表达式匹配合适格式的网页url，继续请求
		next_pages = re.findall(r'http://[a-z]{1,7}.163.com/\d{2}/\d{4}/\d{2}/\w{16}.html',response.body)
		for next_page in next_pages:
			next_page = response.urljoin(next_page)
			yield scrapy.Request(next_page, callback=self.parse)