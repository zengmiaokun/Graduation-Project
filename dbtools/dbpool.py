# -*- coding: utf-8 -*-
"""
Create pool and operate database using DBUtils
"""

import MySQLdb
from DBUtils.PooledDB import PooledDB


class mdpool():
    def __init__(self, host, user, passwd, database, port = 3306):
        self.pool = PooledDB(
            creator=MySQLdb,  # Database connection driver
            maxconnections=0,  # Maximum number of connections allowed. `0` and `None` means unlimited
            mincached=10,  # At initialization, at least free links created in the link pool. `0` means not to create
            maxcached=20,  # Maximun number of  idle links in the connection pool. `0` and `None` means unlimited
            maxusage=None,  # Maximum number of times a connection has been reused. `None` means unlimited
            host=host,
            port=int(port),
            user=user,
            password=passwd,
            database=database,
            charset='utf8'
        )

    def get_conn_cursor(self):
        conn = self.pool.connection()
        cursor = conn.cursor()
        return conn, cursor

    def fetch_one(self, sql, args=()):
        conn, cursor = self.get_conn_cursor()
        cursor.execute(sql, args)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

    def fetch_all(self, sql, args=()):
        conn, cursor = self.get_conn_cursor()
        cursor.execute(sql, args)
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    def insert_one(self, sql, args=()):
        conn, cursor = self.get_conn_cursor()
        res = cursor.execute(sql, args)
        conn.commit()
        print(res)
        conn.close()
        return res

    def update(self, sql, args=()):
        conn, cursor = self.get_conn_cursor()
        res = cursor.execute(sql, args)
        conn.commit()
        print(res)
        conn.close()
        return res


if __name__ == "__main__":
    pass