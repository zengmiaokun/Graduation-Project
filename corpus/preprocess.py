# -*- coding: utf-8 -*-

import re
import string
import jieba
import jieba.posseg
import jieba.analyse

# main
def main(data: iter):
    sw_set = get_sw()
    for item in data:
        # Chinese word segmentation
        res = segment(item[0])
        res = clean(res, sw_set)
        print(res)

def segment(corpus: str) -> list:
    words_list = re.sub('[%s]' % re.escape(string.punctuation + r'\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）'), '', corpus)
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
    


if __name__ == "__main__":
    import sys
    sys.path.append("../")
    from dbtools.dbpool import mdpool

    # Create connection pool of Database
    dbconfig = {'host': 'localhost', 'user': 'test',
                'passwd': 'password', 'port': 3306, 'database': 'corpus'}
    testdb = mdpool(**dbconfig)

    # Get data
    data = testdb.fetch_all(r"SELECT `corpus` FROM `corpus_data`")

    main(data)