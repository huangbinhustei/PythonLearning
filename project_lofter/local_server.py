# -*- coding: utf-8 -*-

from flask import Flask, request
from flask import render_template
import os
from collections import defaultdict
# import base64

app = Flask(__name__)
for_test = "/IMG/"
path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + for_test
pic_dict = defaultdict(lambda: 0)


@app.route("/", methods=["GET", "POST"])
@app.route("/<int:page_id>", methods=["GET", "POST"])
def home(page_id=1):
    post_item = pic_dict[str(page_id)]
    preview_url = "http://192.168.1.101:5000/" + str(page_id - 1)
    next_url = "http://192.168.1.101:5000/" + str(page_id + 1)
    pic_url_fir = post_item[1][0:int(len(post_item[1])/2)]
    pic_url_sec = post_item[1][int(len(post_item[1])/2):]
    print("hah")
    print(pic_url_fir)
    return render_template("home.html", post_item1=pic_url_fir, post_item2=pic_url_sec, p_url=preview_url, n_url=next_url, tit=post_item[0])


if __name__ == "__main__":
    page_number = 0
    for item in os.walk(path):
        pic_path = []
        dir_name = item[0].replace("D:\Project\PythonLearning\project_lofter" + for_test, "")
        for temp in item[2]:
            if temp == "save_log.txt":
                continue
            temp = (item[0] + "/" + temp).replace("D:\\Project\\PythonLearning\\project_lofter/", "http://192.168.1.101/")
            pic_path.append(temp)
        pic_dict[str(page_number)] = [dir_name, pic_path]
        page_number += 1

    app.run(host="192.168.1.101", debug=True)
