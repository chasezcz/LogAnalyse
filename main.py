#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    :   2020/09/11 22:51:22
# @Author  :   Chengze Zhang
# @File    :   main.py
# @Contact :   chengze1996@gmail.com
# Here put the import lib.

import pandas as pd
import numpy as np
import os
from config.config import Config
from logUtils.httpEvent import HttpEvent
from logUtils.session import Session
from classify.logClassify import clustering


def getFilesByPath(path):
    """
    用来获取指定路径下的所有文件
    :param path: 指定的路径
    :return: 所有文件的绝对路径列表
    """
    allfiles = list()
    for root, dirs, files in os.walk(path):
        for f in files:
            allfiles.append(os.path.join(root, f))
    return allfiles


def preSolve(files):
    """
    用来将所有的日志进行合并，先按照 userId，再按照 header，最后按照时间
    :param files: 所有输入的文件
    :return: None
    """
    users = dict()
    # 遍历所有文件
    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            # 按行读取
            while True:
                line = f.readline()  # 逐行读取
                if not line:  # 到 EOF，返回空字符串，则终止循环
                    break
                try:
                    he = HttpEvent(line, True)
                    if not he.userId in users:
                        users[he.userId] = list()
                    users[he.userId].append(he)

                except Exception as e:
                    continue

    originData = list()
    trainingData = list()

    userDataPath = os.path.join(Config.getValue("dataPath"), "output", "users")

    if Config.getValue("isSortByUsers"):
        if not os.path.exists(userDataPath):
            os.makedirs(userDataPath)

    for user in users:
        sessions = Session.getSessionsFromHttpEvents(users[user])
        filename = os.path.join(
            userDataPath, "{0}-{1}.log".format(sessions[0].httpEvents[0].name, user))

        for session in sessions:
            originData.extend(session.getOriginData())
            trainingData.extend(session.getTrainData())
            if Config.getValue("isSortByUsers"):
                with open(filename, "a+", encoding="utf-8") as target:
                    target.writelines(session.getOriginData())
                    target.write("\n")

    outputDataPath = os.path.join(
        Config.getValue("dataPath"), "output", "trainData")
    if not os.path.exists(outputDataPath):
        os.makedirs(outputDataPath)

    # 保存排序好的原日志
    with open(os.path.join(outputDataPath, "originLog.log"), "w", encoding="utf-8") as f:
        f.writelines(originData)

    # 保存训练所用的信息
    with open(os.path.join(outputDataPath, "dates.txt"), "w", encoding="utf-8") as f:
        for line in trainingData:
            f.write("{0}\n".format(line[0]))
    with open(os.path.join(outputDataPath, "urls.txt"), "w", encoding="utf-8") as f:
        for line in trainingData:
            ss = line[1].split("/")
            for s in ss:
                if s != "":
                    f.write(s + " ")
            f.write("\n")
    with open(os.path.join(outputDataPath, "parameters.txt"), "w", encoding="utf-8") as f:
        for line in trainingData:
            ss = line[2].strip("[").strip("]").replace("\"", "").split(",")
            count = 0
            for s in ss:
                if s != "":
                    count += 1
                    f.write(s + " ")
            if count == 0:
                f.write("null")
            f.write("\n")

    with open(os.path.join(outputDataPath, "methods.txt"), "w", encoding="utf-8") as f:

        for line in trainingData:
            f.write(str(line[3])+"\n")

    return originData


def sortOriginData(originData, labels, dimension, numOfClusters):
    clusters = dict()
    for i, label in enumerate(labels):
        if not label in clusters:
            clusters[label] = []
        clusters[label].append(HttpEvent(originData[i], True))

    resultPath = os.path.join(
        Config.getValue("dataPath"), "output/model/{0}-{1}/result.csv".format(dimension, numOfClusters))
    labels = "clusterIndex, date, user, url, params, params_value, header, ip:port"

    with open(resultPath, "w", encoding="utf-8") as f:
        f.write(labels+"\n")
        for clusterId in range(numOfClusters):
            sessions = Session.getSessionsFromHttpEvents(clusters[clusterId])
            for session in sessions:
                for he in session.httpEvents:
                    f.write("{0},{1}".format(clusterId, he.simplyPrint()))
                f.write("\n")
            f.write("\n")


if __name__ == "__main__":
    originData = []
    files = getFilesByPath(os.path.join(
        Config.getValue("dataPath"), "origin"))

    if Config.getValue("generateTrainingData"):
        originData = preSolve(files)
    else:
        with open(os.path.join(Config.getValue("dataPath"), "output", "trainData", "originLog.log"), 'r', encoding="utf-8") as target:
            originData = target.read().splitlines()
    # print(len(originData))

    print("开始聚类")
    if Config.getValue("isCluster"):
        dimension, numOfClusters = 100, 95
        labels, inertia = clustering(dimension, numOfClusters, os.path.join(
            Config.getValue("dataPath"), "output"))

        if len(labels) != len(originData):
            print("数据不匹配, originData: {0}, labels: {1}".format(
                len(originData), len(labels)))
        else:
            sortOriginData(originData, labels, dimension, numOfClusters)
``
