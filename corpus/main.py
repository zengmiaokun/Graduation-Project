# -*- coding: utf-8 -*-

import numpy
import sys
sys.path.append("../")
from dbtools.dbpool import mdpool

resCluster = numpy.load('../data/corpus_cluster.npy')
labelId = [i.split('[')[1].split(',')[0] for i in resCluster]

# Create connection pool of Database
dbconfig = {'host': 'localhost', 'user': 'test',
            'passwd': 'password', 'port': 3306, 'database': 'corpus'}
testdb = mdpool(**dbconfig)

# Get data
data_all = testdb.fetch_all(r"SELECT * FROM `corpus_data` WHERE article_id in %s", (labelId,))
numpy.savetxt('../data/label_data.csv', data_all, fmt='%s', delimiter = ',,,')
