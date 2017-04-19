import os
from aip import AipNlp
from aip import AipOcr
import json
from apps import app_id

basedir = os.path.abspath(os.path.dirname(__file__))


def get_app_info():
    with open(os.path.join(basedir, "APPID.json"), "r") as f:
        return json.loads(f.read())


def emotion_detection():
    aipNlp = AipNlp(app_id["APP_ID"], app_id["API_KEY"], app_id["SECRET_KEY"])
    for item in ["特斯拉外观很漂亮", "特斯拉外形很时尚"]:
        print(item)
        ret = aipNlp.commentTag(item)
        print(ret)


def ocr_detection():
    aipOcr = AipOcr(app_id["APP_ID"], app_id["API_KEY"], app_id["SECRET_KEY"])
