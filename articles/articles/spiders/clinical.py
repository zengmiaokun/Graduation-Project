#-*- coding: utf-8 -*-
import scrapy, json
# from urllib.parse import unquote
from articles.items import ArticlesItem

# 杂志 ID ：名称 
mag_names = {}

class ClinicalSpider(scrapy.Spider):
    name = 'clinical'
    allowed_domains = ['wanfangdata.com.cn']
    start_urls = ['http://c.wanfangdata.com.cn/Category/Magazine/search']

    def start_requests(self):
        #注意 这是原先的
        # for url in self.start_urls:
        #     #直接发送get请求
        #     # yield scrapy.Request(url=url,callback=self.parse)
        formdata ={
            "query": [],
            "start": 0,
            "rows": 10,
            "sort_field": {
                "sort_field": "ImpactFactor"
            },
            "highlight_field": "",
            "pinyin_title": [],
            "class_code": "R4",
            "core_periodical": [],
            "sponsor_region": [],
            "publishing_period": [],
            "publish_status": "",
            "return_fields": [
                "Title",
                "Id",
                "CorePeriodical",
                "Award",
                "PublishStatus"
            ]
        }
 
        #重写父类的方法start_urls
        for url in self.start_urls:
            #直接发送get请求
            yield scrapy.Request(url, method="POST", body=json.dumps(formdata),callback=self.mag_parse)

    def mag_parse(self, response):
        mag_list = json.loads(response.body_as_unicode())['value']
        for mag in mag_list:
            # print("准备爬取期刊《%s》" % mag['Title'][0])
            id = mag['Id']
            mag_names[id] = mag['Title'][0]
            # print(mag_names)
            mag_url = "http://www.wanfangdata.com.cn/perio/detail.do?perio_id=" + id
            yield scrapy.Request(url=mag_url,callback=self.redir_parse)
    def redir_parse(self, response):
        # if response.status == 200:
        #     print("成功打开期刊《%s》详情页" % response.xpath('//a[@class="person-name"]/text()').get())
        real_url = response.url + "/?tabId=article"
        yield scrapy.Request(url=real_url,callback=self.api_parse)

    def api_parse(self, response):
        id = response.xpath('//iframe[@class="perio-info-right"]/@src').get().split('=')[-1]
        years = ['2019', '2018', '2017', '2016', '2015']
        months = list(range(13))[1:]
        api_url = "http://www.wanfangdata.com.cn/sns/third-web/per/perio/articleList?"
        for year in years:
            for month in months:
                paras = "page=1&pageSize=1000&perioId=" + id + "&title=&publishYear=" + year + "&issueNum=" + str(month) + "&otherYear="
                yield scrapy.Request(url=api_url+paras, callback=self.article_parse)

    def article_parse(self, response):
        if response.status == 200:
            # name = json.loads(response.body_as_unicode())['pageRow'][0]['perio_title']
            count = json.loads(response.body_as_unicode())['totalRow']
            # year = response.url.split('=')[-3].split('&')[0]
            # month = response.url.split('=')[-2].split('&')[0]
            # print("\n成功打开API\n期刊名称：%s\n年份刊次：%s年%s期\n文章数：%d" % (name, year, month, count))
            url = "http://www.wanfangdata.com.cn/details/detail.do?"
            for i in range(count):
                paras = "_type=perio&id=" + json.loads(response.body_as_unicode())['pageRow'][i]['article_id']
                # print(url + paras)
                yield scrapy.Request(url=url+paras, callback=self.detail_parse)

    def detail_parse(self, response):
        # print("Page of detail is OK!")
        url = ''
        data = response.xpath('//a[@id="ddownb"]/@onclick').get()

        if "up" in data:
            paras = data.split("'")[1:-1:2]

            if len(paras) == 7:
                paras.append('null')
            paras.append(paras[-2])
            paras = tuple(paras)
            url = "http://www.wanfangdata.com.cn/search/downLoad.do?page_cnt=%s&resourceId=%s&language=%s&source=%s&resourceTitle=%s&isoa=%s&resourceType=%s&first=%s&type=%s" % paras
        else:
            paras = data.split("'")[1:-1:2]

            if len(paras) == 7:
                paras.append('null')
            paras.append(paras[2])
            paras = tuple(paras)
            url = "http://www.wanfangdata.com.cn/search/downLoad.do?page_cnt=%s&language=%s&resourceType=%s&source=%s&resourceId=%s&resourceTitle=%s&isoa=%s&first=%s&type=%s" % paras

        yield scrapy.Request(url=url, callback=self.down_parse)

    def down_parse(self, response):
        # if response.status == 200:
        #     print("进入下载页面")
        # else:
        #     print("无法进入下载页面")

        url = response.xpath('//iframe[@id="downloadIframe"]/@src').get()
        yield scrapy.Request(url=url, callback=self.parse)
        

    def parse(self, response):
        # if response.status == 200:
        #     print("成功解析下载地址")
        # else:
        #     print("下载地址解析失败")

        item = ArticlesItem()
        url = response.url
        item['file_urls'] = [url]
        yield item
        
