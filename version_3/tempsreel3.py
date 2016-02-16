# -*- coding: utf-8 -*-

import sys
import re
import thread
from threading import Thread
import time
import datetime
from datetime import datetime
import math
import requests
import gevent
import grequests
import HTMLParser
import json
from bs4 import BeautifulSoup, SoupStrainer
from pymongo import MongoClient
import pymongo
import inspect
from cgi import escape

def mainPage():
	s = requests.Session()
	url_base = "https://www.jeuxvideo.com/forums/0-"
	#id_forum = input("Forum id: ")
	id_forum = 1000021
	url_middle = "-0-1-0-"
	#url_page = input("Forum page: ")
	url_page = 1
	url_end = "-0-communaute.htm"
	# Main loop
	while 1:
		url = url_base + str(id_forum) + url_middle + str(url_page) + url_end
		print url
		r = singleRequest(url, s)
		topic_list = get25Topics(r)
		fromLastPage(topic_list, s)
		url_page+=25
	return

def singleRequest(url, s):
	try:
		r = s.request('GET', url, timeout=5)
		return r
	except:
		try:
			r = s.request('GET', url, timeout=5)
			return r
		except:
			print "Could not request this url: " + url
			pass

def get25Topics(r):
	strainer = SoupStrainer('ul', {'class': re.compile(r'\btopic-list\b')})
	container_topics = BeautifulSoup(r.text, "html.parser", parse_only=strainer)
	topics = container_topics.find_all('li')
	topic_list = []
	for topic in topics:
		topic_name = topic.find('a', 'lien-jv topic-title')
		if topic_name:
			topic_link = topic_name['href']
			topic_nbmsg = topic.find('span', 'topic-count')
			topic_nbmsg = topic_nbmsg.text.replace(' ', '').replace('\n', '')
			if topic_nbmsg:
				topic_nbpage = float(topic_nbmsg) / 20
				topic_nbpage = int(math.ceil(topic_nbpage))
	                if topic_nbpage == 0:
	                    topic_nbpage = 1
	                topic_lastpage = topic_link.split('-')
	                topic_lastpage[3] = str(topic_nbpage + 1)
	                topic_lastpage = '-'.join(topic_lastpage)
	                topic_list.append('https://www.jeuxvideo.com' + topic_lastpage)
	print len(topic_list)
	return topic_list

def fromLastPage(link_list, s):
	i = 0
	while int(link_list[i].split('-')[3]) > 1:
		previous = link_list[i].split('-')
		previous_page = int(previous[3])
		previous_page -= 1
		previous[3] = str(previous_page)
		link_list[i] = '-'.join(previous)
		print link_list[i]
		res = singleRequest(link_list[i], s)
		#if get_messages(res) == 1:
			#break
		i+=1)
	return

mainPage()
