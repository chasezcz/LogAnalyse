import logging
import os.path
import sys
import multiprocessing
import numpy as np
import joblib
from logUtils.logger import log
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score

from config.config import Config


def clustering(data, dimension: int, numOfClusters: int):

    modelDataPath = os.path.join(Config.getValue(
        "dataPath"), "output", "model", "{0}-{1}".format(dimension, numOfClusters))

    if not os.path.exists(modelDataPath):
        os.makedirs(modelDataPath)

    log("正在聚类")
    # 如果样本量小于 1w，则使用默认的聚类方法
    estimator = KMeans(n_clusters=numOfClusters,
                       algorithm="full", n_jobs=-1, copy_x=False)  # 构造聚类器，分为100类

    # 如果样本量大于 1w，使用分批次聚类方法
    # estimator = MiniBatchKMeans(
    #     n_clusters=numOfClusters, batch_size=Config.getValue("batch"))

    estimator.fit(data)  # 聚类

    labelPred = estimator.labels_  # 获取聚类标签
    centroids = estimator.cluster_centers_  # 获取聚类中心
    inertia = estimator.inertia_  # 获取聚类准则的总和
    # 轮廓系数
    silhouette = silhouette_score(data, labelPred, metric="euclidean")
    # CH 系数
    calinskiHarabaz = calinski_harabasz_score(data, labelPred)
    joblib.dump(estimator, os.path.join(
        modelDataPath, "model-{0}.pkl".format(inertia)))

    clusters = [0 for i in range(numOfClusters)]
    for i, label in enumerate(labelPred):
        clusters[label] += 1

    countFile = os.path.join(modelDataPath, "count.csv")

    with open(countFile, 'w') as fw:  # 聚类结果写入

        fw.write("clusterIndex, numsOfVectors \n")

        for i in range(numOfClusters):
            fw.write("{0},{1}\n".format(i, clusters[i]))

    return labelPred, inertia, silhouette, calinskiHarabaz
