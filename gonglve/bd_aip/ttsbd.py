import os
import requests as req
from apps import get_tok, basedir


def make_mp3(resp, ind):
    if "err_msg" in resp.json():
        print(resp.json()["err_msg"])
        return
    with open(os.path.join(basedir, "res", str(ind) + ".wav"), "wb") as f:
        f.write(resp.content)


class MyTTS:
    def __init__(self, file_name, c_uid=""):
        tok = get_tok()
        if not tok:
            print("INIT ERROR: NO TOKEN")
            return
        if not os.path.exists(file_name):
            print("NO FILE")
            return
        self.api_url = "http://tsn.baidu.com/text2audio"
        self.api_params = {'ctp': 1, 'cuid': c_uid if c_uid else "PPT2VIDEO", 'lan': 'zh', 'tex': '', 'spd': 7,
                           "tok": tok}
        with open(file_name, "r") as f:
            self.texts = [line.strip() for line in f.readlines() if len(line) > 5]

    def run(self):
        for index, item in enumerate(self.texts):
            self.api_params["tex"] = item
            r = req.get(self.api_url, params=self.api_params)
            make_mp3(r, index)


if __name__ == '__main__':
    file = os.path.join(basedir, "daxue.txt")
    tts = MyTTS(file, "FORTEST")
    tts.run()

