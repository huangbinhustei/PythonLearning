# -*- coding: utf-8 -*-

import requests
from collections import defaultdict
import re
import time
from pyquery import PyQuery as pq
import os
import json
import logging

url = "http://192.168.1.101:5000"
data = dict(page_number="9", type="source_url")

i_get = requests.get(url, data)
print(i_get.text)

