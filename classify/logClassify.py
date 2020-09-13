import logging
import os.path
import sys
import multiprocessing
import numpy as np

from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence

from sklearn.cluster import KMeans
from sklearn.externals import joblib


dataPath = ""


def word2vec(dimension: int, modelDataPath: str):
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

    projectNames = ["dates.txt", "methods.txt", "parameters.txt", "urls.txt"]

    for name in projectNames:
        input = os.path.join(dataPath, "trainData", name)
        output = os.path.join(modelDataPath, name+".vector")

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
        model = Word2Vec(LineSentence(input), size=dimension, window=10,
                         min_count=1, workers=multiprocessing.cpu_count())
        # model.save(out1)
        # #不以C语言可以解析的形式存储词向量
        model.wv.save_word2vec_format(output, binary=False)


# 例子data = np.random.rand(100, 8) #生成一个随机数据，样本大小为100, 特征数为8
def get_word_embeddings(is_delete_label, word_embeddings_file):  # 获得word_embeddings
    word_embeddings = {}
    f = open(word_embeddings_file, encoding='utf-8')
    flag = True
    for line in f:
        # 把第一行的内容去掉
        if is_delete_label and flag:
            flag = False
            continue

        values = line.split()
        # 第一个元素是词语
        word = values[0]
        embedding = np.asarray(values[1:], dtype='float32')
        word_embeddings[word] = embedding

    f.close()
    # print("一共有" + str(len(word_embeddings)) + "个词。")
    return word_embeddings


def get_sentences(sentences_file):  # 获得句子 list
    with open(sentences_file, 'r') as fs:
        sentences = fs.readlines()
    return sentences


# sentences is list ，获得句向量
def get_sentence_vector(sentences, word_embeddings, dimension, stopwords=None):
    sentence_vectors = []  # 句子向量
    for i in sentences:
        if len(i) != 0:
            v = sum([word_embeddings.get(w, np.random.uniform(0, 1, dimension))
                     for w in i]) / (len(i) + 0.001)
        else:
            v = np.random.uniform(0, 1, dimension)
        sentence_vectors.append(v)
    return sentence_vectors


def get_sent_vec(is_delete_label, word_embeddings_file, sentences_file, dimension):
    word_embeddings = get_word_embeddings(
        is_delete_label, word_embeddings_file)
    sentences = get_sentences(sentences_file)
    sent_vec = get_sentence_vector(
        sentences, word_embeddings, dimension=dimension)
    return sent_vec

# ------------------------------------文件路径参数-----------------------------------------------------------
# .vector和.txt文件路径


def combineVector(modelDataPath, dimension):
    trainDataPath = os.path.join(dataPath, "trainData")
    params_word_embeddings_file = os.path.join(
        modelDataPath, "parameters.txt.vector")
    params_sentences_file = os.path.join(trainDataPath, "parameters.txt")

    methods_word_embeddings_file = os.path.join(
        modelDataPath, 'methods.txt.vector')
    methods_sentences_file = os.path.join(
        trainDataPath, 'methods.txt')  # methods 的文本的 文件路径

    urls_word_embeddings_file = os.path.join(modelDataPath, 'urls.txt.vector')
    urls_sentences_file = os.path.join(
        trainDataPath, 'urls.txt')  # url 的文本的 文件路径

    dates_word_embeddings_file = os.path.join(
        modelDataPath, "dates.txt.vector")
    dates_sentences_file = os.path.join(trainDataPath, "dates.txt")

# ----------------------------------获得句向量------------------------------------------------------
    # 获得params句向量
    params_sent_vec = get_sent_vec(
        True, params_word_embeddings_file, params_sentences_file, dimension)
    # 获得methods句向量
    methods_sent_vec = get_sent_vec(
        True, methods_word_embeddings_file, methods_sentences_file, dimension)
    # 获得url句向量
    urls_sent_vec = get_sent_vec(
        True, urls_word_embeddings_file, urls_sentences_file, dimension)

    # 获得url、methods、params共同作为操作行为的句向量
    seg_sent_vec = []  # 操作参数为：url、methods和params的三个加权平均
    for i in range(len(params_sent_vec)):
        a_sent_vec = (params_sent_vec[i] +
                      methods_sent_vec[i]+urls_sent_vec[i])/3
        seg_sent_vec.append(a_sent_vec)

    # 获得dates句向量
    dates_sent_vec = get_sent_vec(
        True, dates_word_embeddings_file, dates_sentences_file, dimension)

    # 获得dates、操作行为 共同作为一条消息的句向量
    all_sent_vec = []  # 共为：dates和操作参数的加权平均
    for i in range(len(seg_sent_vec)):
        a_sent_vec = (seg_sent_vec[i]+dates_sent_vec[i])/2
        all_sent_vec.append(a_sent_vec)
    return all_sent_vec


def clustering(dimension: int, numOfClusters: int, path):
    global dataPath
    dataPath = path
    modelDataPath = os.path.join(
        dataPath, "model", "{0}-{1}".format(dimension, numOfClusters))
    if not os.path.exists(modelDataPath):
        os.makedirs(modelDataPath)

    word2vec(dimension, modelDataPath)

    data = combineVector(modelDataPath, dimension)

    estimator = KMeans(n_clusters=numOfClusters,
                       algorithm="full")  # 构造聚类器，分为100类
    estimator.fit(data)  # 聚类

    labelPred = estimator.labels_  # 获取聚类标签
    centroids = estimator.cluster_centers_  # 获取聚类中心
    inertia = estimator.inertia_  # 获取聚类准则的总和

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

    return labelPred, inertia
