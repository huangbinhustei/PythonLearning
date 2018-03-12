import re

from viewer import DBSession, Art


def get_json():
    par = re.compile("<.+?>")
    s_par = "[<>]"

    with open("/Users/baidu/Downloads/用所选项目新建的文件夹2/news.txt", "r") as f:
        cont = f.readlines()

    article = dict()
    s = DBSession()

    for line in cont:
        line = line.strip()
        tmp = re.findall(par, line)
        key = re.sub(s_par, "", tmp[0])
        words = re.sub(par, "", line)

        if key == "contenttitle":
            article["title"] = words
        elif key == "content" or key == "url" or key == "docno":
            article[key] = words
        elif key == "/doc":
            new_art = Art(
                title=article["title"],
                url=article["url"],
                content=article["content"]
            )
            s.add(new_art)
    s.commit()
    s.close()


if __name__ == '__main__':
    if False:
        get_json()
    else:
        print("不要调用这个函数了")