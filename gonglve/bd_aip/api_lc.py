import os
import requests as req
from aip import AipAntiPorn
from aip import AipFace
from aip import AipOcr
from aip import AipNlp
from apps import get_tok, basedir, app_id
import logging
logging.basicConfig(level=logging.ERROR)


def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()


class MyTTS:
    def __init__(self, file_name, c_uid="", output_dir="res"):
        tok = get_tok()
        if not tok:
            logging.error("INIT ERROR: NO TOKEN")
            return
        if not os.path.exists(file_name):
            logging.error("NO FILE")
            return
        self.api_url = "http://tsn.baidu.com/text2audio"
        self.api_params = {'ctp': 1, 'cuid': c_uid if c_uid else "PPT2VIDEO", 'lan': 'zh', 'tex': '', 'spd': 7,
                           "tok": tok}
        self.output_dir = os.path.join(basedir, output_dir)
        with open(file_name, "r") as f:
            self.texts = [line.strip() for line in f.readlines() if len(line) > 5]

    def make_mp3(self, resp, ind):
        if "err_msg" in resp.json():
            logging.error(resp.json()["err_msg"])
            return
        with open(os.path.join(self.output_dir, str(ind) + ".wav"), "wb") as f:
            f.write(resp.content)

    def run(self):
        for index, item in enumerate(self.texts):
            self.api_params["tex"] = item
            r = req.get(self.api_url, params=self.api_params)
            self.make_mp3(r, index)


class MyNlp:
    def __init__(self):
        self.nlp = AipNlp(app_id["APP_ID"], app_id["API_KEY"], app_id["SECRET_KEY"])

    def emotion_detection(self, content):
        ret = self.nlp.commentTag(item)
        return ret


class MyOcr:
    def __init__(self):
        self.ocr = AipOcr(app_id["APP_ID"], app_id["API_KEY"], app_id["SECRET_KEY"])

    def detection(self, pic_path):
        result = self.ocr.general(get_file_content(pic_path))
        if result["words_result_num"] == 0:
            return
        word = ""
        for w in result["words_result"]:
            word += w["words"]
        return word


def func_ocr():
    t_root = "/Users/baidu/Documents/百度/Git/PythonLearning/gonglve/family/static"
    ocr = MyOcr()
    for pardir, folders, files in os.walk(t_root):
        pics = [item for item in files if ".jpg" in item]
        for pic in pics:
            pic_path = os.path.join(pardir, pic)
            print(ocr.detection(pic_path))


def func_tts():
    file = os.path.join(basedir, "daxue.txt")
    tts = MyTTS(file, "FORTEST")
    tts.run()

if __name__ == '__main__':
    func_ocr()
