#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    :   2020/09/23 16:09:43
# @Author  :   Chengze Zhang
# @File    :   logger.py
# @Contact :   chengze1996@gmail.com
# Here put the import lib.
from datetime import datetime


def log(message):
    string = "{0} - {1}".format(
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        message
    )
    print(string)


if __name__ == "__main__":
    log("woefio")
