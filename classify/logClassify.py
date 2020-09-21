import logging
import os.path
import sys
import multiprocessing
import numpy as np
import joblib

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score

from config.config import Config


def word2vec(trainData, dimension: int, modelDataPath: str):
    """ 根据维度生成向量文件
    :param dimension: 生成的向量文件 
    :return: none
    """
    program = "word2vec"

    logger = logging.getLogger(program)

    # %(asctime)s: 打印日志的时间
    # %(levelname)s: 打印日志级别名称
    # %(message)s: 打印日志信息
    logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    logging.root.setLevel(level=logging.ERROR)

    models, vectors = dict(), list()
    # 分别训练词向量
    for name in trainData:
        '''
        LineSentence(inp)：格式简单：一句话=一行; 单词已经过预处理并被空格分隔。
        size：是每个词的向量维度； 
        window：是词向量训练时的上下文扫描窗口大小，窗口为5就是考虑前5个词和后5个词； 
        min-count：设置最低频率，默认是5，如果一个词语在文档中出现的次数小于5，那么就会丢弃； 
        workers：是训练的进程数（需要更精准的解释，请指正），默认是当前运行机器的处理器核数。这些参数先记住就可以了。
        sg ({0, 1}, optional) – 模型的训练算法: 1: skip-gram; 0: CBOW
        alpha (float, optional) – 初始学习率
        iter (int, optional) – 迭代次数，默认为5
        '''
        models[name] = Word2Vec(
            trainData[name], size=dimension, window=10, min_count=1)
        # 模型保存
        # model[name].wv.save_word2vec_format(output, binary=False)

    def getSentenceVector(sentence, name):
        words = sentence.split(" ")
        vector = sum(
            [
                models[name][word] if word in models[name] else np.random.uniform(0, 1, dimension) for word in words
            ]
        ) / (len(words) + 0.01)
        if len(sentence) == 0 or sentence == "null":
            vector = np.random.uniform(0, 1, dimension)

        return vector

    # 合成句向量
    for index in range(len(trainData)):

        line = trainData.loc[index]
        vector = (getSentenceVector(line["dates"], "dates") + (
            (getSentenceVector(line["urls"], "urls") +
             getSentenceVector(line["parameters"], "parameters") +
             getSentenceVector(line["methods"], "methods")
             )/3.0)
        )/2.0
        vectors.append(vector)

    return vectors


def clustering(trainData, dimension: int, numOfClusters: int):

    modelDataPath = os.path.join(Config.getValue(
        "dataPath"), "output", "model", "{0}-{1}".format(dimension, numOfClusters))

    if not os.path.exists(modelDataPath):
        os.makedirs(modelDataPath)

    data = word2vec(trainData, dimension, modelDataPath)

    # 如果样本量小于 1w，则使用默认的聚类方法
    # estimator = KMeans(n_clusters=numOfClusters,
    #                    algorithm="full")  # 构造聚类器，分为100类

    # 如果样本量大于 1w，使用分批次聚类方法
    estimator = MiniBatchKMeans(
        n_clusters=numOfClusters, batch_size=Config.getValue("batch"))

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
