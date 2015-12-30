# -*- coding: utf-8 -*-

import sys
import re
import thread
import time
import datetime
import requests
import HTMLParser
import thread
from bs4 import BeautifulSoup

def get_forum():
	forum1 = "http://m.jeuxvideo.com/forums/0-51-0-1-0-"
	forum2 = 1
	forum3 = "-0-blabla-18-25-ans.htm"
	i = 0
	r = requests.Session()
	while 1:
		s = r.request('GET', forum1 + str(forum2) + forum3);
		# s = requests.get(forum1 + str(forum2) + forum3);
		status = s.elapsed;
		print status;
		forum2+=25
		i+=1
		if i > 25:
			return
	return

get_forum();