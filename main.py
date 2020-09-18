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
import matplotlib.pyplot as plt


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
            for line in f:
                try:
                    he = HttpEvent(line, True)
                except Exception as e:
                    continue
                users[he.userId].append(he) if (
                    he.userId in users) else users.setdefault(he.userId, list())

    # 如果按照user分割的话，创建对应文件夹
    userDataPath = os.path.join(Config.getValue("dataPath"), "output", "users")
    if Config.getValue("isSortByUsers"):
        if not os.path.exists(userDataPath):
            os.makedirs(userDataPath)

    originData, trainDataList = list(), list()

    for user in users:
        sessions = Session.getSessionsFromHttpEvents(users[user])
        filename = os.path.join(
            userDataPath, "{0}-{1}.log".format(sessions[0].httpEvents[0].name, user))

        for session in sessions:
            originData.extend(session.getOriginData())
            trainDataList.extend(session.getTrainData())

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

    trainData = pd.DataFrame(data=trainDataList,  columns=[
        "dates", "urls", "parameters", "methods"])
    trainData.to_csv(os.path.join(outputDataPath, "data.csv"))
    return originData, trainData


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
    originData, trainData = [], []
    files = getFilesByPath(os.path.join(
        Config.getValue("dataPath"), "origin"))

    if Config.getValue("generateTrainingData"):
        originData, trainData = preSolve(files)
    else:
        if Config.getValue("isCombineCSV"):
            with open(os.path.join(Config.getValue("dataPath"), "output", "trainData", "originLog.log"), 'r', encoding="utf-8") as target:
                originData = target.read().splitlines()
        trainData = pd.read_csv(
            os.path.join(Config.getValue("dataPath"),
                         "output", "trainData", "data.csv"),
            dtype={"dates": np.str, "urls": np.str, "parameters": np.str, "methods": np.str})

    # print(trainData.head())

    if Config.getValue("isCluster"):
        print("开始聚类")
        # 生成所有要训练的 K 值
        ks = [i for i in range(Config.getValue("numOfClustersStart"), Config.getValue(
            "numOfClustersEnd"), Config.getValue("numOfClustersStep"))]
        inertias, silhouettes, calinskiHarabazs = [], [], []
        dimension = Config.getValue("dimension")

        for numOfClusters in ks:
            print("正在训练，K={0}".format(numOfClusters))
            labels, inertia, silhouette, calinskiHarabaz = clustering(
                trainData, dimension, numOfClusters)

            inertias.append(inertia)
            silhouettes.append(silhouette)
            calinskiHarabazs.append(calinskiHarabaz)

            if Config.getValue("isCombineCSV"):
                if len(labels) != len(originData):
                    print("数据不匹配, originData: {0}, labels: {1}".format(
                        len(originData), len(labels)))
                else:
                    sortOriginData(originData, labels,
                                   dimension, numOfClusters)

        print(ks)
        print(inertias)
        print(silhouettes)
        # 中文和负号的正常显示
        plt.rcParams['font.sans-serif'] = [u'SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        # 设置绘图风格
        plt.style.use('ggplot')
        # 绘制K的个数与轮廓系数的关系

        plt.plot(ks, silhouettes, 'b*-')
        plt.xlabel("k值一簇数量")
        plt.ylabel("轮廓系数")
        plt.savefig(os.path.join(Config.getValue("dataPath"), "output", "model", "silhouttes-{0}.png".format(dimension)), format='png',
                    transparent=True, dpi=300, pad_inches=0)
        plt.clf()

        plt.plot(ks, inertias, 'o-')
        plt.xlabel("k值一簇数量")
        plt.ylabel("Inertia")
        plt.savefig(os.path.join(Config.getValue("dataPath"), "output", "model", "inertia-{0}.png".format(dimension)), format='png',
                    transparent=True, dpi=300, pad_inches=0)
        plt.clf()

        plt.plot(ks, calinskiHarabazs, 'o-')
        plt.xlabel("k值一簇数量")
        plt.ylabel("CH系数")
        plt.savefig(os.path.join(Config.getValue("dataPath"), "output", "model", "calinskiHarabaz-{0}.png".format(dimension)), format='png',
                    transparent=True, dpi=300, pad_inches=0)
