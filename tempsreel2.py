# -*- coding: utf-8 -*-

import sys
import re
import thread
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

DEBUG_MODE = False
client = MongoClient()
# Database
db = client['jvcrawler']
db.pseudo.ensure_index("pseudo", unique = True)
db.jvstalker.ensure_index("ancre", unique = True)

###
# FUNCTIONS
###
def mainPage():
	debugFunction()
	s = grequests.Session()
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
		bulk_request = bulkRequests(topic_list)
		fromLastPage(bulk_request, topic_list)
		del topic_list
		del bulk_request
		del r
		url_page+=25
		
	return

def get25Topics(r):
	start_time = time.time()
	debugFunction()

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
	elapsedTime(start_time)
	return topic_list

def bulkRequests(topic_list):
	start_time = time.time()
	debugFunction()

	try:
		rs = (grequests.get(u, timeout=5) for u in topic_list)
		response = grequests.map(rs)
		return response
	except:
		s = (grequests.get(u, timeout=5) for u in topic_list)
		response = grequests.map(rs)
		return response
	
	elapsedTime(start_time)
	return
	

def fromLastPage(bulk_request, link_list):
	start_time = time.time()
	debugFunction()
	i = 0
	nb_requests = 0
	for res in bulk_request:
		list_pages = []
		while int(link_list[i].split('-')[3]) > 1:
			previous = link_list[i].split('-')
			previous_page = int(previous[3])
			previous_page -= 1
			previous[3] = str(previous_page)
			link_list[i] = '-'.join(previous)
			list_pages.append(link_list[i])
			print link_list[i]
			if nb_requests > 1:
				r = bulkRequests(list_pages)
				if get_messages(r) == 1:
					break
				del list_pages[:]
				nb_requests = 0
			nb_requests+=1
		try:
			res.close()
		except:
			pass
		i+=1
	r = bulkRequests(list_pages)
	if get_messages(r) == 1:
		return

	elapsedTime(start_time)
	return

def parseMessages():
	start_time = time.time()
	debugFunction()

	elapsedTime(start_time)
	return

def insertPseudo(pseudo):
	start_time = time.time()
	debugFunction()
	pseudotoinsert = {"pseudo": pseudo['pseudo'],
                	  "nb_msg": 1}
	try:
		db.pseudo.insert_one(pseudotoinsert).inserted_id
	except:
		pass
		db.pseudo.update_one({'pseudo': pseudo['pseudo']}, {
					  '$inc': {
					    'nb_msg': 1
					  }
					}, upsert=False)
	elapsedTime(start_time)
	return

def insertPost(post):
	start_time = time.time()
	debugFunction()
	try:
		insert_error = 0
		db.jvstalker.insert_one(post).inserted_id
	except:
		insert_error = 1
		pass
	insertPseudo(post)
	elapsedTime(start_time)
	return insert_error

def bulkInsertDatabase(pseudos):
	start_time = time.time()
	debugFunction()
	#Insert post to database
	#db.pseudo.insert_one(pseudo).inserted_id
	try:
		db.pseudo.insert_many(pseudos)
	except:
		pass

	elapsedTime(start_time)
	return

def get_messages(response):
	bloc_message = SoupStrainer('div', {'class': 'bloc-message-forum '})
	for res in response:
		if res == None:
			continue
		soup = BeautifulSoup(res.text, "html.parser", parse_only=bloc_message)
		for s in soup:
			# Pseudo
			pseudo = s.find('span', attrs={'class': 'bloc-pseudo-msg'})
			pseudo = pseudo.getText().replace(' ', '').replace('\n', '')
			#sys.stdout.write(pseudo)
			print pseudo
			# Ancre
			ancre = s['data-id']
			print ancre
			# Message
			message = s.find('div', attrs={'class': 'text-enrichi-forum'}).renderContents()
			print message
			# Date
			date = s.find('div', attrs={'class': 'bloc-date-msg'}).text.replace('\n', '')
			#print date
			date = parse_date(date)
			print date
			# Avatar
			avatar = s.find('img', attrs={'class': 'user-avatar-msg'})
			avatar = avatar['data-srcset'].replace('avatar-sm', 'avatar-md').replace('//image.jeuxvideo.com/', '') # Add 'image.jeuxvideo.com' in frontend
			print avatar
			print "================================================================================================"
			pseudotoinsert = {"pseudo": pseudo, "message": message, "date": date, "ancre": ancre, "avatar": avatar}
			if insertPost(pseudotoinsert) == 1:
 				return 1
		try:
			res.close()
		except:
			pass
	return 0

def parse_date(date):
	p_date = date.split(' ')
	# Encode characters
	d = p_date[0]
	p_date[1] = p_date[1].encode('utf8', 'replace')
	if 'janvier' in p_date[1]:
		m = '01'
	elif 'février' in p_date[1]:
		m = '02'
	elif 'mars' in p_date[1]:
		m = '03'
	elif 'avril' in p_date[1]:
		m = '04'
	elif 'mai' in p_date[1]:
		m = '05'
	elif 'juin' in p_date[1]:
		m = '06'
	elif 'juillet' in p_date[1]:
		m = '07'
	elif 'août' in p_date[1]:
		m = '08'
	elif 'septembre' in p_date[1]:
		m = '09'
	elif 'octobre' in p_date[1]:
		m = '10'
	elif 'novembre' in p_date[1]:
		m = '11'
	elif 'décembre' in p_date[1]:
		m = '12'
	y = p_date[2]
	h = p_date[4].split(':')
	ladate = datetime(int(y), int(m), int(d), int(h[0]), int(h[1]), int(h[2]))
	print ladate
	return ladate

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

###
# DEBUG FUNCTIONS
###
def debugFunction():
	global DEBUG_MODE
	if DEBUG_MODE == True:
		print "Function: " + inspect.stack()[1][3]
	return

def elapsedTime(start_time):
	global DEBUG_MODE
	if DEBUG_MODE == True:
		elapsed_time = time.time() - start_time
		print "Time elapsed: " + str(round(elapsed_time, 4))
	return

# Main function
start_time = time.time()

mainPage()

print "Program ended"
elapsedTime(start_time)






