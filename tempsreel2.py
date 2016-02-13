# -*- coding: utf-8 -*-

import sys
import re
import thread
import time
import datetime
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

DEBUG_MODE = True
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

	rs = (grequests.get(u) for u in topic_list)
	response = grequests.map(rs)
	
	elapsedTime(start_time)
	return response

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
				get_messages(r)
				#get_pseudos(r)
				del list_pages[:]
				nb_requests = 0
			nb_requests+=1
		res.close()
		i+=1
	r = bulkRequests(list_pages)
	#get_pseudos(r)
	get_messages(r)

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
		db.jvstalker.insert_one(post).inserted_id
	except:
		pass
	insertPseudo(post)
	elapsedTime(start_time)
	return

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
	bloc_message = SoupStrainer('div', {'class': 'inner-head-content'})
	bloc_ancre = SoupStrainer('span', {'class': 'bloc-message-forum-anchor'})
	for res in response:
		soup = BeautifulSoup(res.text, "html.parser", parse_only=bloc_message)
		soup_ancre = BeautifulSoup(res.text, "html.parser", parse_only=bloc_ancre)
		ancres = soup_ancre.find_all('span')
		i = 0
		for s in soup:
			# Pseudo
			pseudo = s.find('span', attrs={'class': 'bloc-pseudo-msg'})
			pseudo = pseudo.getText().replace(' ', '').replace('\n', '')
			# Message
			message = s.find('div', attrs={'class': 'text-enrichi-forum'}).renderContents()
			# Date
			date = s.find('div', attrs={'class': 'bloc-date-msg'})
			date = date.text.replace(' ', '').replace('\n', '')
			# Ancre
			ancre = ancres[i]['id'].split('_')[1]
			print ancre
			pseudotoinsert = {"pseudo": pseudo, "message": message, "date": date, "ancre": ancre}
			insertPost(pseudotoinsert)
			i+=1

	return

def get_pseudos(response):
    i = 1
    nb_insert = 0
    print "SIZE OF RES" + str(len(response))
    pseudo = SoupStrainer('div', {'class': 'bloc-header'})
    for link in response:
        if link:
            print str(i) + " ==================================================="
            i+=1
            soup = BeautifulSoup(link.text, "html.parser", parse_only=pseudo)
            pseudal = soup.find_all('span', attrs={'class':'bloc-pseudo-msg'})
            blocmessage = soup.find_all('div', attrs={'class':'text-enrichi-forum'})
            message = blocmessage[i].renderContents()
            list_pseudos = []
            nb_insert = 0
            for pseud in pseudal:
                pseud = pseud.getText().replace(' ', '').replace('\n', '')
                pseudotoinsert = {"pseudo": pseud,
                				  "nb_msg": 1}
                list_pseudos.insert(nb_insert, pseudotoinsert)
                print pseud
                singleInsertDatabase(pseudotoinsert)
                nb_insert+=1
            #print list_pseudos
            #bulkInsertDatabase(list_pseudos)
#            thread.start_new_thread(insertPseudo, (list_pseudos, ))
            #insertPseudo(list_pseudos)
        try:
            link.close()
        except:
            pass

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






