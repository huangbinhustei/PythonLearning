# -*- coding: utf-8 -*-

import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/IMG/"
log_list = []


def file_filter(this_path):
    log_file_name = this_path[1]
    data = []
    set_url_this_page = []  # 这一页的所有图片url

    def row_filter(rows, this_str):
        for temp in rows:
            if not temp[0].find(this_str) == 0:
                continue
            if temp[1] in set_url_this_page:
                continue
            set_url_this_page.append(temp[1])
            data.append(temp)

    if not os.path.exists(log_file_name):
        return
    with open(log_file_name, "r") as old_log:
        t_row = []
        for lines in old_log.readlines():
            temp_row = lines.split("\t")
            t_row.append(temp_row)
        row_filter(t_row, "succeed")
        row_filter(t_row, "has_saved")
        row_filter(t_row, "failed")

    with open(log_file_name, "w") as f:
        for lines in data:
            f.write("\t".join(lines))

if __name__ == '__main__':

    for item in os.walk(path):
        log_list.append([item[0], item[0] + "/save_log.txt"])

    for item in log_list[1:]:
        file_filter(item)