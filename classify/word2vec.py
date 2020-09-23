#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @Time    :   2020/09/23 16:16:22
# @Author  :   Chengze Zhang
# @File    :   word2vec.py
# @Contact :   chengze1996@gmail.com
# Here put the import lib.

import os
import multiprocessing

import numpy as np

from logUtils.logger import log
from config.config import Config
from gensim.models import Word2Vec


def word2vec(trainData, dimension: int):
    """ 根据维度生成向量文件
    :param dimension: 生成的向量文件 
    :return: none
    """
    # program = "word2vec"

    # logger = logging.getLogger(program)

    # # %(asctime)s: 打印日志的时间
    # # %(levelname)s: 打印日志级别名称
    # # %(message)s: 打印日志信息
    # logging.basicConfig(format='%(asctime)s: %(levelname)s: %(message)s')
    # logging.root.setLevel(level=logging.ERROR)
    vectorFileName = os.path.join(Config.getValue("dataPath"), "output",
                                  "vector", "{0}.npy".format(dimension))
    if os.path.exists(vectorFileName):
        vectorss = np.load(vectorFileName)
        log("存在已训练的向量文件，直接读取：" + str(vectorss.shape))
        return vectorss
    else:
        os.makedirs(os.path.join(Config.getValue(
            "dataPath"), "output", "vector"))

    models, vectors = dict(), list()
    # 分别训练词向量

    log("训练词向量")
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
            trainData[name], size=dimension, window=10, min_count=1, workers=multiprocessing.cpu_count())
        # 模型保存
        # model[name].wv.save_word2vec_format(output, binary=False)

    def getSentenceVector(sentence, name):
        if len(sentence) == 0 or sentence == "null":
            return np.random.uniform(0, 1, dimension)

        words = sentence.split(" ")

        vector = np.zeros(dimension)
        for word in words:
            if word in models[name]:
                vector += models[name][word]
            else:
                vector += np.random.uniform(0, 1, dimension)

        vector /= len(words)

        return vector

    log("合成句向量")
    # 合成句向量
    for index in range(len(trainData)):

        vector = (
            getSentenceVector(trainData.at[index, "dates"], "dates") + (
                (getSentenceVector(trainData.at[index, "urls"], "urls") +
                 getSentenceVector(trainData.at[index, "parameters"], "parameters") +
                 getSentenceVector(trainData.at[index, "methods"], "methods")
                 )/3.0
            )
        )/2.0
        # log(index, vector)
        vectors.append(vector)
    vectorss = np.asarray(vectors)
    np.save(vectorFileName, vectorss)
    return vectors
