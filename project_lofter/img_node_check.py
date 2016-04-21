# -*- coding: utf-8 -*-

from nude import Nude
import os

path = os.path.abspath(os.path.join(os.path.dirname(__file__))) + "/images/"

img_name = "257f5c30f3d3f010e1e383e794866224.jpg"
path += img_name

print(path)
n = Nude(path)
n.parse()
print(n.result)
print(n.inspect())
