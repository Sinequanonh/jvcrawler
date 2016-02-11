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

def mainPage():
	start_time = time.time()
	debugFunction()

	elapsedTime(start_time)
	return

def get25Topics():
	start_time = time.time()
	debugFunction()

	elapsedTime(start_time)
	return

def bulkRequests():
	start_time = time.time()
	debugFunction()

	elapsedTime(start_time)
	return

def fromLastPage():
	start_time = time.time()
	debugFunction()

	elapsedTime(start_time)
	return

def parseMessages():
	start_time = time.time()
	debugFunction()

	elapsedTime(start_time)
	return

def singleInsertDatabase():
	start_time = time.time()
	debugFunction()

	elapsedTime(start_time)
	return

def bulkInsertDatabase():
	start_time = time.time()
	debugFunction()

	elapsedTime(start_time)
	return

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






