import os
from aip import AipNlp
from aip import AipOcr
import json

basedir = os.path.abspath(os.path.dirname(__file__))


def get_app_info():
    with open(os.path.join(basedir, "APPID.json"), "r") as f:
        return json.loads(f.read())


my_app_id = get_app_info()


def emotion_detection():
    aipNlp = AipNlp(my_app_id["APP_ID"], my_app_id["API_KEY"], my_app_id["SECRET_KEY"])
    for item in ["特斯拉外观很漂亮", "特斯拉外形很时尚"]:
        print(item)
        ret = aipNlp.commentTag(item)
        print(ret)


def ocr_detection():
    aipOcr = AipOcr(my_app_id["APP_ID"], my_app_id["API_KEY"], my_app_id["SECRET_KEY"])
