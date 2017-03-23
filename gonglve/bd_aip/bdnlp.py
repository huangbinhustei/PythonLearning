import os
from aip import AipAntiPorn
from aip import AipNlp
import json


basedir = os.path.abspath(os.path.dirname(__file__))
def get_app_info():
    with open(os.path.join(basedir,"APPID.json"), "r") as f:
        return json.loads(f.read())

mydict = get_app_info()

aipNlp = AipNlp(mydict["APP_ID"], mydict["API_KEY"], mydict["SECRET_KEY"])
for item in  ["特斯拉外观很漂亮","特斯拉外形很时尚"]:
	print(item)
	ret = aipNlp.commentTag(item)
	print(ret)




