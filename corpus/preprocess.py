# -*- coding: utf-8 -*-

import re
import string
import numpy
import jieba
import jieba.posseg
import jieba.analyse
from pyhanlp import *

# main
def main(data: iter):
    sw_set = get_sw()
    res_list = []
    for item in data:
        res = list(item)
        # Chinese word segmentation
        res[3] = segment(item[3])
        res[3] = clean(res[3], sw_set)
        res_list.append(res)
        # print(res)

    return res_list

def segment(corpus: str) -> list:
    words_list = re.sub('[%s]' % re.escape(string.punctuation + r'\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）'), '', corpus)
    # jieba.enable_parallel(2)
    return jieba.lcut(words_list, cut_all=False)

def get_sw():
    stopwords = dict()
    with open(r"stopwords/cn_stopwords.txt", 'r') as cn_sw:
        stopwords['cn_sw_list'] = cn_sw.read().splitlines()
    with open(r"stopwords/baidu_stopwords.txt", 'r') as baidu_sw:
        stopwords['baidu_sw_list'] = baidu_sw.read().splitlines()
    with open(r"stopwords/hit_stopwords.txt", 'r') as hit_sw:
        stopwords['hit_sw_list'] = hit_sw.read().splitlines()
    with open(r"stopwords/scu_stopwords.txt", 'r') as scu_sw:
        stopwords['scu_sw_list'] = scu_sw.read().splitlines()

    print('\nLoading stopwords\n' + '='*30)
    sw_list = []
    for k,v in stopwords.items():
        print("%-15s -> %d" % (k, len(v)))
        sw_list += v
    sw_set = set(sw_list)
    print('%-15s -> %d' % ('Total', len(sw_set)))
    print('='*30 + '\n')
    return sw_set

def clean(words_list: list, sw_set: set) -> str:
    # Load stopwords
    res = []
    for word in words_list:
        if word in sw_set:
            continue
        res.append(word)
    return res
    

def cluster(data: dict, mean = 'kmeans', para = 300) -> list:
    ClusterAnalyzer = JClass('com.hankcs.hanlp.mining.cluster.ClusterAnalyzer')
    analyzer = ClusterAnalyzer()
    for k,v in data.items():
        analyzer.addDocument(k,v)
    print("PASS")
    return analyzer.kmeans(para) if mean == 'kmeans' else analyzer.repeatedBisection(para) 

if __name__ == "__main__":
    import sys
    sys.path.append("../")
    from dbtools.dbpool import mdpool

    # Create connection pool of Database
    dbconfig = {'host': 'localhost', 'user': 'test',
                'passwd': 'password', 'port': 3306, 'database': 'corpus'}
    testdb = mdpool(**dbconfig)

    # Get data
    data_all = testdb.fetch_all(r"SELECT * FROM `corpus_data`")
    # res_all = main(data_all)
    # numpy.save('corpus', res_all, allow_pickle=True, fix_imports=True)
    
    raw_data = numpy.load('corpus.npy', allow_pickle=True)
    data = dict()
    for item in raw_data:
        if str(item[1]) not in data.keys():
            data[str(item[1])] = item[3]
        else:
            data[str(item[1])] += item[3]
    for k, v in data.items():
        data[k] = ', '.join(v)
    res = [i.toString() for i in cluster(data).toArray()]
    numpy.save('corpus_cluster', res, allow_pickle=True, fix_imports=True)