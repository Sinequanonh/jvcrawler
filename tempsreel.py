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

### CONNECT TO THE DATABASE
def insertPseudo(pseudo):
    # Mongod instance
    client = MongoClient()
    # Database
    db = client['jvcrawler']
    #Insert post to database
    #db.pseudo.insert_one(pseudo).inserted_id
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
        link_list = []
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
                    print topic_author
                    topic_nbmsg = topic.find('span', 'topic-count')
                    topic_nbmsg = topic_nbmsg.text.replace(' ', '').replace('\n', '')
                    if topic_nbmsg:
                        print topic_nbmsg
                        topic_nbpage = float(topic_nbmsg) / 20
                        topic_nbpage = int(math.ceil(topic_nbpage))
                        if topic_nbpage == 0:
                            topic_nbpage = 1
                        print topic_nbpage
                        # Assign last page of the topic
                        topic_lastpage = topic_link.split('-')
                        topic_lastpage[3] = str(topic_nbpage)
                        topic_lastpage = '-'.join(topic_lastpage)
                        print topic_lastpage
                        link_list.append('https://www.jeuxvideo.com/' + topic_lastpage)
                        
            print "================================================"
        # Async requests the 25 topics all in once
        rs = (grequests.get(u) for u in link_list)
        response = grequests.map(rs)
        get_pages(response, topics, link_list)

#        get_pseudos(response)
        i+=1
        return

# from the first page of a topic
def get_pages(response, topics, link_list):
    i = 0
    nb_link = 0
    nb_requests = 0
    for res in response:
        # get each page from the last
        list_pages = []
        while int(link_list[i].split('-')[3]) > 0:
            previous = link_list[i].split('-')
            previous_page = int(previous[3])
            previous_page -= 1
            previous[3] = str(previous_page)
            link_list[i] = '-'.join(previous)
            list_pages.append(link_list[i])
            print link_list[i]
            if nb_requests > 4:
                rs = (grequests.get(u) for u in list_pages)
                laresponse = grequests.map(rs)
                get_pseudos(laresponse)
                nb_requests = 0
                del list_pages[:]
            nb_requests+=1
            
        rs = (grequests.get(u) for u in list_pages)
        laresponse = grequests.map(rs)
        get_pseudos(laresponse)
        res.close()
        i+=1
    return
        
    
def get_post():
    return

def get_pseudos(response):
    i = 1
    nb_insert = 0
    print "SIZE OF RES" + str(len(response))
    pseudo = SoupStrainer('div',{'class': 'bloc-header'})
    for link in response:
        print str(i) + " ==================================================="
        i+=1
        soup = BeautifulSoup(link.text, parseOnlyThese=pseudo)
        pseudal = soup.find_all('span', attrs={'class':'bloc-pseudo-msg'})
        list_pseudos = []
        for pseud in pseudal:
            pseud = pseud.getText().replace(' ', '').replace('\n', '')
            pseudotoinsert = {"pseudo": pseud}
            list_pseudos.insert(nb_insert, pseudotoinsert)
            #insertPseudo(pseudotoinsert)
            nb_insert+=1
        print list_pseudos
        insertPseudo(list_pseudos)

        

start_time = time.time()
crawler()
elapsed_time = time.time() - start_time
print elapsed_time
