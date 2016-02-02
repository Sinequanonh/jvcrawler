# -*- coding: utf-8 -*-

import sys
import re
import thread
import time
import datetime
import requests
import HTMLParser
from bs4 import BeautifulSoup
from pymongo import MongoClient
import pymongo

### CONNECT TO THE DATABASE
def connectDatabase():
    # Mongod instance
    client = MongoClient()
    # Database
    db = client['jvcrawler']
    post = {
        "Pseudo": "Glosoli",
        "Sexe": "Male",
        "Messages": 28584
        }
    # Insert post to database
    db.pseudo.insert_one(post).inserted_id

def crawler():
    s = requests.Session()
    i = 0
    while i < 20:
        # Request the main page
        try:
            r = s.request('GET', 'https://www.jeuxvideo.com', timeout=5)
        except:
            try:
                r = s.request('GET', 'https://www.jeuxvideo.com', timeout=5)
            except:
                continue
        soup = BeautifulSoup(r.text, "html.parser")
        print r.status_code
        print r.elapsed
        i+=1

crawler()
#connectDatabase()
