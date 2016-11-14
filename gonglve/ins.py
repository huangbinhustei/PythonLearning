import requests as req
from pyquery import PyQuery as pq

url = "https://www.instagram.com/angelababyct/"
proxies = {
	'http': "socks5://127.0.0.1:1080",
	'https': "socks5://127.0.0.1:1080"
	}

r = req.get(url,proxies=proxies)
print(pq(r.content).text())