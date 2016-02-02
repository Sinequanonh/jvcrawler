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
    pseudo = {"pseudo": pseudo}
    # Insert post to database
    db.pseudo.insert_one(pseudo).inserted_id

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
        # Parse the content
        a_tag = SoupStrainer('a')
        a_tags = [tag for tag in BeautifulSoup(r.text, parseOnlyThese=a_tag)]
        topic25 = 0
        link_list = []
        for line in a_tags:
            if "forums/42" in line['href']:
                print line['href']
                topic_link = line['href'].replace('/forums/', 'https://www.jeuxvideo.com/forums/')
                link_list.insert(topic25, topic_link)
                topic25+=1
            if topic25 > 23:
                break
        rs = (grequests.get(u) for u in link_list)
        # Async request the 25 topics all in once
        response = grequests.map(rs)
        get_pseudos(response)
        i+=1

def get_pseudos(response):
    i = 0
    for link in response:
        pseudo = SoupStrainer('div',{'class': 'bloc-header'})
        soup = BeautifulSoup(link.text, parseOnlyThese=pseudo)
        pseudal = soup.find_all('span', attrs={'class':'bloc-pseudo-msg'})
        for pseud in pseudal:
            pseud = pseud.getText().replace(' ', '').replace('\n', '')
            print pseud
            insertPseudo(pseud)
        i+=1
        print str(i) + " =================="

start_time = time.time()
crawler()
elapsed_time = time.time() - start_time
print elapsed_time
#connectDatabase()
