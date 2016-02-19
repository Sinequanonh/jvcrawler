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

red = "\033[31m";
green = "\033[32m";
magenta = "\033[35m";
cyan = "\033[36m";
blue = "\033[34m";
yellow = "\033[33m";
white = "\033[0m";

client = MongoClient(maxPoolSize=50, waitQueueMultiple=10)
# Database
db = client['jvcrawler']
# pseudo
db.pseudo.ensure_index("pseudo", unique = True)
# jvstalker
db.bla1825.ensure_index("ancre", unique = True)
# galerie
db.galerie.ensure_index("shack", unique = True)
db.galerie.ensure_index("pseudo")
# vocaroo
db.vocaroo.ensure_index("vocaroo", unique = True)

def mainPage():
	s = requests.Session()
	url_base = "https://www.jeuxvideo.com/forums/0-"
	#id_forum = input("Forum id: ")
	id_forum = 51
	url_middle = "-0-1-0-"
	url_page = input("Forum page: ")
	#url_page = 1
	url_end = "-0-blabla-18-25-ans.htm"
	# Main loop
	while 1:
		url = url_base + str(id_forum) + url_middle + str(url_page) + url_end
		#print red + url + white
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
			topic_nbmsg = int(topic_nbmsg) + 1
			if topic_nbmsg:
				topic_nbpage = float(topic_nbmsg) / 20
				topic_nbpage = int(math.ceil(topic_nbpage))
				if topic_nbpage == 0:
					topic_nbpage = 1
				topic_lastpage = topic_link.split('-')
				topic_lastpage[3] = str(topic_nbpage + 1)
				topic_lastpage = '-'.join(topic_lastpage)
				topic_list.append('https://www.jeuxvideo.com' + topic_lastpage)
	return topic_list

def fromLastPage(link_list, s):
	i = 0
	while i < 24:
		while int(link_list[i].split('-')[3]) > 1:
			previous = link_list[i].split('-')
			previous_page = int(previous[3])
			previous_page -= 1
			previous[3] = str(previous_page)
			link_list[i] = '-'.join(previous)
			#print cyan + link_list[i] + white
			res = singleRequest(link_list[i], s)
			if get_messages(res) == 1:
				break
		i+=1
	return

def get_messages(response):
	if response == None:
		return 0
	bloc_message = SoupStrainer('div', {'class': 'bloc-message-forum '})
	soup = BeautifulSoup(response.text, "html.parser", parse_only=bloc_message)
	for s in soup:
		if s == None:
			continue
		# Pseudo
		try:
			pseudo = s.find('span', attrs={'class': 'bloc-pseudo-msg'})
			pseudo = pseudo.getText().replace(' ', '').replace('\n', '')
		except:
			pseudo = "Pseudo supprimé"
		#sys.stdout.write(pseudo)
		#print pseudo
		# Ancre
		ancre = s['data-id']
		#print ancre
		# Message
		message_raw = s.find('div', attrs={'class': 'text-enrichi-forum'})
		message = message_raw.renderContents()
		message_raw = message_raw.getText()
		message_raw = ' '.join(message_raw.split())
		#print message_raw
		nb_mots = len(message_raw.split(' '))
		nb_chars = len(message_raw)
		#print message
		#print "nb mots: " + str(nb_mots)
		#print message
		# Smileys
		nb_smileys = 0
		try:
			del smiley_list
		except:
			pass
		if "data-def=\"SMILEYS\"" in message:
			smileys = BeautifulSoup(message, "html.parser")
			les_smileys = smileys.find_all('img', attrs={'data-def': 'SMILEYS'})
			smiley_list = {}
			for smiley in les_smileys:
				smi = smiley['src'].replace('//', '')
				#print smiley['alt']
				smi = smi.split('/')[2].replace('.gif', '')
				if smiley_list.has_key(str(smi)):
					smiley_list[str(smi)]+=1
				else:
					smiley_list[str(smi)] = 1
				nb_smileys+=1
			#print smiley_list
		# Date
		date = s.find('div', attrs={'class': 'bloc-date-msg'}).text.replace('\n', '').replace('"', '').lstrip()
		#print date
		#print date
		date = parse_date(date)
		#print date
		# Avatar
		try:
			avatar = s.find('img', attrs={'class': 'user-avatar-msg'})
			avatar = avatar['data-srcset'].replace('avatar-sm', 'avatar-md').replace('//image.jeuxvideo.com/', '') # Add 'image.jeuxvideo.com' in frontend
		except:
			avatar = ""
		#print avatar
		# Get vocaroo
		if "vocaroo" in message:
			vocaroo = BeautifulSoup(message, "html.parser")
			#print "Un vocaroo ! " + str(ancre)
			vocarooall = vocaroo.find_all('span', attrs={'class', 'JvCare'})
			#print vocarooall
			for vo in vocarooall:
				if "vocaroo.com/" in vo.text:
					voca = vo.text.split('/')[4]
					vocarootoinsert = {"pseudo": pseudo, "date": date, "ancre": ancre, "vocaroo": voca}
					print blue + voca + white
					insertVocaroo(vocarootoinsert)

		# Get puu.sh links
		if "puu.sh" in message:
			puush = BeautifulSoup(message, "html.parser")
			puushall = puush.find_all('span', attrs={'class', 'JvCare'})
			#print vocarooall
			for pu in puushall:
				if "puu.sh/" in pu.text:
					pus = pu.text.split('/')[4]
					print cyan + pus + white
					puushtoinsert = {"pseudo": pseudo, "date": date, "ancre": ancre, "shack": pus, "type": False}
					insertGalerie(puushtoinsert)

		# Galerie - Get noelshacks
		if "noelshack.com" in message:
			noelshack = BeautifulSoup(message, "html.parser")
			try:
				les_noels = noelshack.find_all('a', attrs={'data-def': 'NOELSHACK'})
				for le_noel in les_noels:
					shack = str(le_noel.img['src']).replace('//image.noelshack.com/minis/', '') # Add 'image.noelshack.com/minis/' in frontend for a miniature
																								# Add 'http://image.noelshack.com/fichiers/' in frontend for fullpicture
					noelshacktoinsert = {"pseudo": pseudo, "date": date, "ancre": ancre, "shack": shack, "type": True}
					insertGalerie(noelshacktoinsert)
			except:
				pass
		#print "================================================================================================"
		pseudotoinsert = {"pseudo": pseudo, "message": message, "date": date, "ancre": ancre, "avatar": avatar, "nb_smileys": nb_smileys, "nb_mots": nb_mots, "nb_chars": nb_chars}
		try:
			1#insertSmileys(smiley_list, pseudo)
		except:
			pass
		#thread.start_new_thread(insertPost, (pseudotoinsert,))
		# thread1 = Thread(target=insertPost, args=(pseudotoinsert,))
		# thread1.start()
	 #   	thread1.join()
		if insertPost(pseudotoinsert) == 1:
			#print red + "None" + white 
			return 1
		else:
			1
			#print magenta + pseudo + yellow + ' ' + str(date) + white
	# try:
	# 	res.close()
	# except:
	# 	pass
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
	return ladate

def insertPost(post):
	try:
		db.jvstalker.insert_one(post).inserted_id
		insertPseudo(post)
		return 0
	except:
		return 1

def insertVocaroo(vocaroo):
	try:
		db.vocaroo.insert_one(vocaroo).inserted_id
	except:
		pass

def insertPseudo(pseudo):
	pseudotoinsert = {"pseudo": pseudo['pseudo'],
                	  "nb_msg": 1,
                	  "nb_smileys": int(pseudo['nb_smileys']),
                	  "nb_mots": int(pseudo['nb_mots']),
                	  "nb_chars": int(pseudo['nb_chars']),
                	  "avatar": pseudo['avatar']
                	  }
	try:
		db.pseudo.insert_one(pseudotoinsert).inserted_id
	except:
		db.pseudo.update_one({'pseudo': pseudo['pseudo']}, {
					  '$inc': {
					    'nb_msg': 1,
					    'nb_smileys': int(pseudo['nb_smileys']),
					    "nb_mots": int(pseudo['nb_mots']),
					    "nb_chars": int(pseudo['nb_chars'])
					  }
					}, upsert=False)
	return

def insertGalerie(shack):
	try:
		db.galerie.insert_one(shack).insert_id
	except:
		pass
	return

mainPage()
