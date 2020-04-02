# -*- coding: utf-8 -*-

import numpy
import sys
sys.path.append("../")
from dbtools.dbpool import mdpool

resCluster = numpy.load('../data/corpus_cluster.npy')
labelId = resCluster.split('[')[1].split(',')[0]

# Create connection pool of Database
dbconfig = {'host': 'localhost', 'user': 'test',
            'passwd': 'password', 'port': 3306, 'database': 'corpus'}
testdb = mdpool(**dbconfig)

# Get data
data_all = testdb.fetch_all(r"SELECT * FROM `corpus_data` WHERE article_id in %s", labelId)