# -*- coding: utf-8 -*-
# !/usr/bin/python
"""
-------------------------------------------------
   File Name：     GetFreeProxy.py
   Description :  抓取免费代理
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: 
                   这一部分考虑用scrapy框架代替
-------------------------------------------------
"""
import re
import requests

try:
    from importlib import reload   #py3 实际不会实用，只是为了不显示语法错误
except:
    import sys     # py2
    reload(sys)
    sys.setdefaultencoding('utf-8')




from Util.utilFunction import robustCrawl, getHtmlTree, getHTMLText
from header import random_header

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()

HEADER = random_header


class GetFreeProxy(object):
    """
    proxy getter
    """

    def __init__(self):
        pass

    @staticmethod
    @robustCrawl
    def freeProxyFirst():
        """
        抓取米扑代理 http://proxy.mimvp.com/api/fetch.php?orderid=860170713165250819
        ：return:
        """
        url = 'http://proxy.mimvp.com/api/fetch.php?orderid=860170713165250819'
        html = getHTMLText(url, headers=HEADER())
        proxy_list = html.split('\r\n')
        for proxy in proxy_list:
            yield proxy

    @staticmethod
    @robustCrawl
    def freeProxySecond(proxy_number=100):
        """
        抓取代理66 http://www.66ip.cn/
        :param proxy_number: 代理数量
        :return:
        """
        url = "http://m.66ip.cn/mo.php?sxb=&tqsl={}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=".format(
            proxy_number)

        html = getHTMLText(url, headers=HEADER())
        for proxy in re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html):
            yield proxy

    @staticmethod
    @robustCrawl
    def freeProxyThird(days=1):
        """
        抓取有代理 http://www.youdaili.net/Daili/http/
        :param days:
        :return:
        """
        url = "http://www.youdaili.net/Daili/http/"
        tree = getHtmlTree(url)
        page_url_list = tree.xpath('.//div[@class="chunlist"]/ul/li/p/a/@href')[0:days]
        for page_url in page_url_list:
            html = requests.get(page_url, headers=HEADER()).content
            # print html
            proxy_list = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}', html)
            for proxy in proxy_list:
                yield proxy

    @staticmethod
    @robustCrawl
    def freeProxyFourth():
        """
        抓取西刺代理 http://api.xicidaili.com/free2016.txt
        :return:
        """
        url_list = ['http://www.xicidaili.com/nn',  # 高匿
                    'http://www.xicidaili.com/nt',  # 透明
                    ]
        for each_url in url_list:
            tree = getHtmlTree(each_url)
            proxy_list = tree.xpath('.//table[@id="ip_list"]//tr')
            for proxy in proxy_list:
                yield ':'.join(proxy.xpath('./td/text()')[0:2])

    @staticmethod
    @robustCrawl
    def freeProxyFifth():
        """
        抓取guobanjia http://www.goubanjia.com/free/gngn/index.shtml
        :return:
        """
        url = "http://www.goubanjia.com/free/gngn/index{page}.shtml"
        for page in range(1, 10):
            page_url = url.format(page=page)
            tree = getHtmlTree(page_url)
            proxy_list = tree.xpath('//td[@Class="ip"]')
            for each_proxy in proxy_list:
                # yield ''.join(each_proxy.xpath('.//span[not @Style="display: none;"]//text()'))
                ips = each_proxy.xpath('.//span[not (@Style="display: none;")]//text()|.//div[not (@Style="display: none;")]//text()')
                ip = ''.join(ips[0:-1])
                yield ':'.join([ip,ips[-1]])

if __name__ == '__main__':
    gg = GetFreeProxy()
    # for e in gg.freeProxyFirst():
    #     print e

    # for e in gg.freeProxySecond():
    #     print e

    # for e in gg.freeProxyThird():
    #     print e
    #
    # for e in gg.freeProxyFourth():
    #     print e

    for e in gg.freeProxyFifth():
        print(e)