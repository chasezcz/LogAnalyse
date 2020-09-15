#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/11 23:35
# @Author  : Chengze Zhang
# @File    : httpEvent.py
# Here put the import lib

import datetime


class HttpEvent(object):

    def __init__(self, originLog: str, saveOriginData: bool):
        """
        初始化 httpEvent
        :param originLog: 原始日志
        :param saveOriginData: 是否保存原始日志
        """
        super().__init__()
        splits = originLog.split(" ")
        content = list()

        for s in splits:
            s = s.strip()
            if s == "":
                continue
            content.append(s)
        if content[2] == "ERROR" or len(content) < 14:
            raise Exception("错误日志")
        try:
            tmpDate = "{0} {1}".format(content[0], content[1])
            # 时间
            self.date = datetime.datetime.strptime(
                tmpDate, '%Y-%m-%d %H:%M:%S,%f')
        except Exception as identifier:
            raise identifier

        self.threadId = content[7]
        self.institutionId = content[8]
        self.userId = content[9]
        self.url = content[10]
        self.method = content[11]
        # 参数
        self.parameter = content[14]
        self.parameterValue = "".join(content[i]
                                      for i in range(15, len(content)-4))
        self.parameterValue.replace(" ", ",")
        self.port = content[len(content) - 1]
        self.ip = content[len(content) - 2]
        self.name = content[len(content) - 3]
        self.header = content[len(content) - 4].replace(" ", ",")

        originLog = " ".join(
            [" ".join(content[:14]),
             self.parameterValue,
             self.header,
             self.name,
             self.ip,
             self.port,
             "\n"]
        )
        if saveOriginData:
            self.originLog = originLog

    def simplyPrint(self):
        return "{0},{1}-{2},{3},{4},{5},{6},{7}:{8}\n".format(
            self.date.strftime('%Y-%m-%d %H:%M:%S.%f'),
            self.userId,
            self.name,
            self.url,
            self.parameter,
            self.parameterValue.replace(",", "..", ),
            self.header,
            self.ip,
            self.port)


if __name__ == '__main__':
    log = '2020-09-03 08:05:25,790  INFO cn.arp.icas.authorize2.log.LogAspect - ICAS-LOG | 5152 310111 149492352b734619a613f2b1b593cdfb /fa/commoncore/todoCommonCore/remoteGetTotalTodoNum GET 200 [] [] [] [{"httpOnly":false,"maxAge":-1,"name":"Authorization","secure":false,"value":"abwgBq4nAGJa","version":0}] 文印室 159.226.99.33 35396'
    # [{"criteria":[],   "offset":0,    "limit":10}]
    he = HttpEvent(log, True)
    # print(he)
    print(he.userId)
