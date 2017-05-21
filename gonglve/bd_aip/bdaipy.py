import os
from aip import AipAntiPorn
from aip import AipFace
from aip import AipOcr
import time
from PIL import Image
from collections import defaultdict
from apps import app_id

basedir = os.path.abspath(os.path.dirname(__file__))


aipFace = AipFace(app_id["APP_ID"], app_id["API_KEY"], app_id["SECRET_KEY"])
aipAntiPorn = AipAntiPorn(app_id["APP_ID"], app_id["API_KEY"], app_id["SECRET_KEY"])
root = os.path.join(basedir, "static")


def _1024_check():
    res = []
    for pardir, folders, files in os.walk(root):
        pics = [item for item in files if ".jpg" in item]
        for pic in pics:
            pic_path = os.path.join(pardir, pic)
            result = aipAntiPorn.detect(get_file_content(pic_path))
            if "result" in result:
                writeln = [pic_path]
                final = [pic]
                for item in result["result"]:
                    writeln.append(item["class_name"])
                    writeln.append(str(item["probability"]))
                    if item["class_name"] == "正常":
                        final.append(str(item["probability"]))
                print("\t".join(final))
                with open(os.path.join(basedir, "res.txt"), "a") as f:
                    f.write("\t".join(writeln) + "\n")
            else:
                print(result)
            time.sleep(1)


def get_file_content(file_path):
    with open(file_path, 'rb') as fp:
        return fp.read()


def get_small_file_content(file_path):
    thumbnail_name = "thumb_" + os.path.basename(file_path)
    img = Image.open(file_path)
    w, h = img.size
    a = min(500 / max(w, h), 1)
    nw, nh = int(w * a), int(h * a)
    img.thumbnail((nh, nw))
    img.save(thumbnail_name, "jpeg")
    new_path = os.path.abspath(os.path.join(file_path, os.pardir, os.pardir, thumbnail_name))
    return new_path


def group_by_result(pic_list):
    def get_file_path(_ind):
        return pic_list[int(_ind)].replace(root, "")

    if len(pic_list) >= 2:
        result = aipFace.match(map(get_file_content, pic_list))
        b = defaultdict(set)
        print(result)
        for item in result["results"]:
            if item["score"] > 80:
                b[item["index_i"]].add(item["index_j"])

        final_list = []
        for k, v in b.items():
            v.add(k)
            final_list.append(v)
        for index, item in enumerate(final_list):
            for s_index, s_item in enumerate(final_list[index + 1:]):
                if item & s_item:
                    item |= s_item
                    final_list.remove(s_item)
        final = []
        for item in final_list:
            final.append(set(map(get_file_path, item)))
        print(final)


def img_group():
    for pardir, folders, files in os.walk(root):
        pics = [os.path.join(pardir, item) for item in files if ".jpg" in item and len(item) == 5]
    group_by_result(pics)





if __name__ == '__main__':
    # img_group()
    _1024_check()
    # ocr_detection()
