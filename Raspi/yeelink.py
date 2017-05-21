#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import json
from config import API, HEADERS


def get_cpu_temp():
    with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
        temp = float(f.read()) / 1000
    return {"value": temp}


def get_gpu_temp():
    gpu = os.popen('/opt/vc/bin/vcgencmd measure_temp').read()
    ret = gpu.strip().replace('temp=', '').replace('\'C', '')
    temp = float(ret)
    return {"value": temp}


def posting():
    s.post(API["CPU_Temperature"], data=json.dumps(get_cpu_temp()))
    s.post(API["GPU_Temperature"], data=json.dumps(get_gpu_temp()))

if __name__ == '__main__':
    s = requests.session()
    s.headers = HEADERS
    posting()

