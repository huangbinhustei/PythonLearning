import requests
import os
from base64 import b64encode as b64e
from aip import AipAntiPorn
import aip
import time

s = requests.session()
basedir = os.path.abspath(os.path.dirname(__file__))
pics = ["1.jpg","2.jpg","3.jpg","4.jpg","5.jpg","6.jpg","7.jpg","8.jpg","9.jpg","10.jpg","11.jpg","12.jpg","13.jpg","14.jpg","15.jpg","16.jpg"]
imgs = []

APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
# for item in pics:
# 	with open(os.path.join(basedir, "static", item),"rb") as f:
# 		imgs.append(b64e(f.read()))

def comp_by_file():
	url_dectect = "https://api-cn.faceplusplus.com/facepp/v3/detect"
	url_compile = "https://api-cn.faceplusplus.com/facepp/v3/compare"
	da = dict([("api_key", "nn75NkGOezE-ESf581OUF_VcWZQIW5VT"),("api_secret","y5BNHGhwT9PEnMXF6aksYgF-1aAu6guu")])
	fi = {"image_file1":p1,"image_file2":p2}
	r = requests.post(url_compile,params=da,files=fi)
	if r.status_code == 200:
		print(r.json())


def get_token_bd():
	secret = {
		"grant_type": "client_credentials",
		"client_id": "glv5e5uwaCwsDd9v6eggQzna",
		"client_secret": "NnUafCbvdt7YRBmC6eORM49rjh7D7lFN",
	}
	url_for_token = "https://openapi.baidu.com/oauth/2.0/token"
	r1 = s.get(url_for_token, params=secret)

	if r1.status_code == 200:
		return r1.json()["access_token"]
	else:
		return False

def aip_by_bd():
	aipAntiPorn = AipAntiPorn(APP_ID, API_KEY, SECRET_KEY)

	for item in pics:
		time.sleep(1)
		with open(os.path.join(basedir, "static", item),"rb") as f:
			result = aipAntiPorn.detect(f.read())
			print(type(result))
			print(result["result"])
			break
	


def comp_baidu(token):
	url = "https://aip.baidubce.com/rest/2.0/faceverify/v1/match"
	files = {"images": b",".join(imgs)}
	params = {"access_token": token}
	r = requests.post(url, params=params, files=files)
	print(r.json())

def get_age_and_rank(token):
	url = "https://aip.baidubce.com/rest/2.0/face/v1/detect"
	params = {"access_token": token}
	files = {"face_fields": "age,beauty"}
	for item in imgs:
		files["image"] = item
		print("size:" + str(len(files["image"])))
		r = s.post(url, params=params, files=files)
		print(r.json().decode("utf-8"))

if __name__ == '__main__':
	tok = get_token_bd()
	if tok:
		# get_age_and_rank(tok)
		aip_by_bd()
	
