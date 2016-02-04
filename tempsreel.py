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
        topics_jvc = SoupStrainer('a', 'lien-jv topic-title')
        topics_jvc = [tag for tag in BeautifulSoup(r.text, parseOnlyThese=topics_jvc)]
        j = 0
        link_list = [] 
        for topic_lien in topics_jvc:
            print topic_lien['href']
            topic_link = topic_lien['href'].replace('/forums/', 'https://www.jeuxvideo.com/forums/')
            link_list.insert(j, topic_link)
            j+=1
        # Async requests the 25 topics all in once
        rs = (grequests.get(u) for u in link_list)
        response = grequests.map(rs)
        get_pages(response)
        get_pseudos(response)
        i+=1
        return

def get_pages(response):
    
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
