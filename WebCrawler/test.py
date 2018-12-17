#!/usr/bin/env python 3.6
# -*- coding: utf-8 -*-
# @Time    : 3/20/18 21:34
# @Author  : Yam
# @Site    : 
# @File    : test.py
# @Software: PyCharm
import hashlib

encrypter = hashlib.md5()
encrypter.update('admin'.encode('utf-8'))
print(encrypter.hexdigest())