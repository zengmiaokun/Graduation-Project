#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import MySQLdb
from corpus.decrypt import decrypt_files
import corpus.extractor as extractor

# Decrypt pdf
decrypt_files(r'articles/Downloads', r'decrypted')
print("Decrypt: have finished")


# Create the Connection of Database
db = MySQLdb.Connect("localhost", "test", "password", "corpus", charset="utf8")
cursor = db.cursor()

# Get list of journals
journals = os.listdir('decrypted/articles/Downloads/')
for journal in journals:
    sql = r"INSERT INTO `journals` (`name`) VALUES (%s)"
    try:
        cursor.execute(sql, (journal,))
        db.commit()
    except:
        # Rollback in case there is any error
        print("Error: %s\nJournal: %s" % ('Insert journal', journal))
        db.rollback()

print("Success: Import journals")

# Import paragraph data
data_gen = extractor.extract_all(r'decrypted')
for element in data_gen:

    # Get journal_id
    try:
        sql = r"SELECT `id` FROM `journals` WHERE `name` = %s"
        cursor.execute(sql, (element['journal'],))
        journal_id = cursor.fetchall()[0][0]
    except:
        print("Error:%s\nJournal:%s\nTitle:%s" %
              ('Get journal_id', element['journal'], element['title']))
    # Insert article data into table articles
    try:
        sql = r"INSERT INTO `articles` (`journal_id`,`title`,`date`) VALUES (%s, %s, %s)"
        cursor.execute(
            sql, (journal_id, element['title'], '%s-%s-01' % (element['year'], element['month']),))
        db.commit()
    except:
        # Rollback in case there is any error
        print("Error:%s\nJournal:%s\nTitle:%s" %
              ('Insert article', element['journal'], element['title']))
        db.rollback()

    # Get article_id
    try:
        sql = r"SELECT `id` FROM `articles` WHERE `title` = %s"
        cursor.execute(sql, (element['title'],))
        article_id = cursor.fetchall()[0][0]
    except:
        print("Error:%s\nJournal:%s\nTitle:%s" %
              ('Get article_id', element['journal'], element['title']))
    # Insert abstraction into table paragraph
    try:
        sql = r"INSERT INTO `paragraph` (`article_id`,`section_id`,`text`) VALUES (%s, %s, %s)"
        cursor.execute(sql, (article_id, '1', element['abstract'],))
        db.commit()
    except:
        # Rollback in case there is any error
        print("Error:%s\nJournal:%s\nTitle:%s" %
              ('Insert abstraction', element['journal'], element['title']))
        db.rollback()
    # Insert discuss into table paragraph
    try:
        sql = r"INSERT INTO `paragraph` (`article_id`,`section_id`,`text`) VALUES (%s, %s, %s)"
        cursor.execute(sql, (article_id, '2', element['discuss'],))
        db.commit()
    except:
        # Rollback in case there is any error
        print("Error:%s\nJournal:%s\nTitle:%s" %
              ('Insert discuss', element['journal'], element['title']))
        db.rollback()

print("Success: Import acstraction and paragraph")


# Split paragraph

db_write = MySQLdb.Connect(
    "localhost", "test", "password", "corpus", charset="utf8")
cursor_write = db_write.cursor()

cursor.execute("SELECT * FROM `paragraph` WHERE `text` != 'NULL'")

while True:
    row = cursor.fetchone()
    if not row:
        break
    for sentence in row[3].split('。'):
        length, length_w = len(sentence), len(re.findall(r'[\u4e00-\u9fa5]', sentence))
        if sentence and sentence != '' and length > 5 and length_w / length > 0.7:
            cursor_write.execute(
                "INSERT INTO `corpus_data` (`article_id`, `section_id`, `corpus`) VALUES (%s, %s, %s)", (row[1], row[2], sentence))
            db_write.commit()

cursor.close()
cursor_write.close()
db.close()
db_write.close
