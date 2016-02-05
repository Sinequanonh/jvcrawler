# -*- coding: utf-8 -*-

import sys
import re
import thread
import time
import datetime
import requests
import gevent
import grequests
import HTMLParser
import json
from bs4 import BeautifulSoup, SoupStrainer
#from BeautifulSoup import BeautifulSoup, SoupStrainer
from pymongo import MongoClient
import pymongo

### CONNECT TO THE DATABASE
def insertPseudo(pseudo):
    # Mongod instance
    client = MongoClient()
    # Database
    db = client['jvcrawler']
    # Insert post to database
#    db.pseudo.insert_one(pseudo).inserted_id
    db.pseudo.insert_many(pseudo)

def crawler():
    s = grequests.Session()
    i = 0
    while i < 1:
        # Request the main page
        try:
            r = s.request('GET', 'https://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm', timeout=5)
        except:
            try:
                r = s.request('GET', 'https://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm', timeout=5)
            except:
                continue
        print str(r.status_code) + " " + str(r.elapsed)
        # get topics from the page
        strainer = SoupStrainer('ul', {'class': re.compile(r'\btopic-list\b')})
        container_topics = BeautifulSoup(r.text, "html.parser", parse_only=strainer)
        les_topics = container_topics.find_all('li')

        # Parse each <li>
        topics = []
        for topic in les_topics:
            #Get info from topic url
            topic_name = topic.find('a', 'lien-jv topic-title')
            if topic_name:
                topic_title = topic_name['title']
                topic_link = topic_name['href']
                print topic_title
                print topic_link
                topic_id = topic_link.split('-')[2]
                print topic_id
            topic_author = topic.find('span', re.compile(r'\btopic-author\b'))
            if topic_author:
                topic_author = topic_author.text.replace(' ', '').replace('\n', '')
                if topic_name:
                    topics.append({
                            'title': topic_title,
                            'url': topic_link,
                            'id': topic_id,
                            'author': topic_author
                            })
            print "======================="


        # Async requests the 25 topics all in once
#        rs = (grequests.get(u) for u in link_list)
 #       responses = grequests.map(rs)

#        get_pseudos(response)
        i+=1
        return

# from the first page of a topic
def get_pages(response):
    nextStrainer = SoupStrainer('div', 'pagi-after')
    next = BeautifulSoup(response.text, parseOnlyThese=nextStrainer)
    print next
#    caca =[tag for tag in BeautifulSoup(response.text, parseOnlyThese=nextStrainer)]
#   for prout in caca:
 #       print prout['href']
    
    return

def get_post():
    return

def get_pseudos(response):
    i = 1
    nb_pseudos = 0
    for link in response:
        print str(i) + " ==================================================="
        i+=1
        pseudo = SoupStrainer('div',{'class': 'bloc-header'})
        try:
            soup = BeautifulSoup(link.text, parseOnlyThese=pseudo)
        except:
            pass
        pseudal = soup.find_all('span', attrs={'class':'bloc-pseudo-msg'})
        list_pseudos = []
        for pseud in pseudal:
            pseud = pseud.getText().replace(' ', '').replace('\n', '')
            print pseud
            pseudotoinsert = {"pseudo": pseud}
            list_pseudos.insert(nb_pseudos, pseudotoinsert)
            nb_pseudos+=1
#        print list_pseudos
        insertPseudo(list_pseudos)

start_time = time.time()
crawler()
elapsed_time = time.time() - start_time
print elapsed_time
