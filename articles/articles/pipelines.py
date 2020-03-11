# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.files import FilesPipeline, md5sum
from io import BytesIO
from urllib.parse import unquote
import os, re
mag_names = {'zhhlzz': '中华护理杂志', 'zgwzbjjyx': '中华危重病急救医学', 'hsjxzz': '护士进修杂志', 'zghlgl': '中国护理管理', 'hlglzz': '护理管理杂志','qiyyj-chcf': '企业研究（策划与财富）', 'syhlzz': '中国实用护理杂志', 'hlxzz': '护理学杂志', 'zgkfyxzz': '中国康复医学杂志', 'cwycnyy': '肠外与肠内营养'}

class MyFilesPipeline(FilesPipeline):

    def file_path(self, request, response=None, info=None):
        url = request.url
        info = re.findall(r'([resourceId]+)=(\w+?)(\d+)', url)[0]
        mag_name = mag_names[info[-2]]
        perio = "%s年%s期" % (info[-1][:4], info[-1][4:6])
        return os.path.join(mag_name, perio)
        

    def file_downloaded(self, response, request, info):
        path = self.file_path(request, response=response, info=info)
        name = str(response.headers.getlist("Content-Disposition")).split('\"')[-2]
        file_name = unquote(name)
        full_path = os.path.join(path, file_name)
        buf = BytesIO(response.body)
        checksum = md5sum(buf)
        buf.seek(0)
        self.store.persist_file(full_path, buf, info)
        if response.status == 200:
            print("下载完成：" + file_name)
        return checksum 

class ArticlesPipeline(object):
    def process_item(self, item, spider):
        return item

