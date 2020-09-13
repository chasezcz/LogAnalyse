#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    :   2020/09/11 23:07:21
# @Author  :   Chengze Zhang 
# @File    :   config.py
# @Contact :   chengze1996@gmail.com
# Here put the import lib.
import json


class Config(object):
    
    @staticmethod
    def getValue(key):
        """
        :param:
        :return:
        """
        with open("config/config.json", "r", encoding="utf-8") as target:
            return json.load(target)[key]

