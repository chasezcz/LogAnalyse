#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/12 22:37
# @Author  : Chengze Zhang
# @File    : session.py
# Here put the import lib

import datetime
from logUtils.httpEvent import HttpEvent

class Session(object):

    def __init__(self, ):
        self.httpEvents = []
        self.firstHttpEventDate = datetime.datetime

    def getOriginData(self):
        originData = list()
        for he in self.httpEvents:
            originData.append(he.originLog)
        return originData

    def getTrainData(self):
        data = list()
        for he in self.httpEvents:
            data.append((int((he.date-self.firstHttpEventDate).microseconds/1000), he.url, he.parameter, he.method))
        return data

    @staticmethod
    def getSessionsFromHttpEvents(httpEvents: [HttpEvent]):
        '''
        在一堆 HttpEvent 中，通过对 header 归类，划分为 Session 的 List，list内部按照 datatime 排序。
        :param httpEvents: 传入的 HttpEvent 列表
        :return: 返回一个 Session 列表
        '''
        sessionsByHeader = dict()
        for he in httpEvents:
            header = he.header
            if header not in sessionsByHeader:
                sessionsByHeader[header] = Session()
            sessionsByHeader[header].httpEvents.append(he)
        sessions = list(sessionsByHeader.values())
        
        def taketime(elem):
            return elem.date.timestamp()

        for session in sessions:
            session.httpEvents.sort(key=taketime)
            # print(len(session))
            session.firstHttpEventDate = session.httpEvents[0].date
        return sessions
