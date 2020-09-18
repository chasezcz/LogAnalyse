#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/11 23:35
# @Author  : Chengze Zhang
# @File    : httpEvent.py
# Here put the import lib

import os
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
        if content[len(content) - 1].isalnum():
            self.port = content[len(content) - 1]
            self.ip = content[len(content) - 2]
            self.name = content[len(content) - 3]
            self.header = content[len(content) - 4].replace(" ", ",")

            self.parameter = content[14]
            self.parameterValue = "".join(content[i]
                                          for i in range(15, len(content)-4))

        else:
            self.port = "0"
            self.ip = content[len(content) - 1]
            self.name = content[len(content) - 2]
            self.header = content[len(content) - 3].replace(" ", ",")
            self.parameter = content[14]
            self.parameterValue = "".join(content[i]
                                          for i in range(15, len(content)-3))

        self.parameterValue.replace(",", "..")

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

        # for test
        self.length = len(content)

    def simplyPrint(self):
        return "{0},{1}-{2},{3},{4},{5},{6},{7}:{8}\n".format(
            self.date.strftime('%Y-%m-%d %H:%M:%S.%f'),
            self.userId,
            self.name,
            self.url,
            self.parameter,
            self.parameterValue,
            self.header,
            self.ip,
            self.port)


if __name__ == '__main__':
    path = "data/origin"
    allfiles = list()
    for root, dirs, files in os.walk(path):
        for f in files:
            allfiles.append(os.path.join(root, f))

    leng = {}
    with open("error.log", "w", encoding="utf-8") as target:

        for file in allfiles:
            with open(file, 'r', encoding='utf-8') as f:
                # 按行读取
                for line in f:
                    try:
                        he = HttpEvent(line, True)
                        # if he.length not in leng:
                        #     leng[he.length] = 0
                        # leng[he.length] += 1
                    except Exception as e:
                        # target.write(line)
                        pass
                    if " " in he.parameterValue:
                        print(line + "错误")
                    if he.parameterValue.startswith("[") and he.parameterValue.endswith("]"):
                        pass
                    else:
                        print(line + "WW")
                    # if he.ip not in leng:
                    #     leng[he.ip] = 0
                    # leng[he.ip] += 1
                    # target.write("{0}:{1}\n".format(he.ip, he.port))
        # for key, value in leng.items():
        #     target.write("{0}: {1}\n".format(key, value))
    # while True:
    #     line = f.readline()  # 逐行读取
    #     if not line:  # 到 EOF，返回空字符串，则终止循环
    #         break
    #     try:
    #         he = HttpEvent(line, True)
    #         if not he.userId in users:
    #             users[he.userId] = list()
    #         users[he.userId].append(he)

    #     except Exception as e:
    #         continue
