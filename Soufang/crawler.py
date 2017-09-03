# -*- coding: utf-8 -*-

#################################### update ####################################
# 201707072250 第一个版本

#################################### import ####################################
import requests
import pandas as pd
from numpy.random import rand
from bs4 import BeautifulSoup

#################################### crawler ###################################
URL = 'http://esf.sh.fang.com'

def randHeader():
    head_connection = ['Keep-Alive', 'close']
    head_accept = ['text/html, application/xhtml+xml, */*']
    head_accept_language = ['zh-CN,fr-FR;q=0.5', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']
    head_user_agent = ['Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                       'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219 Firefox/2.0.0.12 Navigator/9.0.0.6',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000 Chrome/26.0.1410.43 Safari/537.1 ',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92 Safari/537.1 LBBROWSER',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 TaoBrowser/3.0 Safari/536.11',
                       'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                       'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0'
                       ]
    result = {
        'Connection': head_connection[0],
        'Accept': head_accept[0],
        'Accept-Language': head_accept_language[1],
        'User-Agent': head_user_agent[int(rand()*len(head_user_agent))]
    }
    return result

def get_dist_urls(url):
    data = requests.get(url, headers=randHeader())
    soup = BeautifulSoup(data.text, 'html.parser')
    urls = soup.select('div[class="qxName"]')[0].select('a')[1:19]
    urls = {u.get_text(): URL+u.get('href') for u in urls}
    return urls

def get_cbd_urls(url):
    data = requests.get(url, headers=randHeader())
    soup = BeautifulSoup(data.text, 'html.parser')
    urls = soup.select('p[id="shangQuancontain"]')[0].select('a')[1:]
    urls = {u.get_text(): URL+u.get('href') for u in urls}
    return urls

def get_info(url):
    data = requests.get(url, headers=randHeader())
    soup = BeautifulSoup(data.text, 'html.parser')
    info = soup.select('p[class="setNum"]')
    quant = info[0].get_text()
    price = info[1].get_text()
    return price, quant

##################################### main #####################################
def main():
    INFO = pd.DataFrame(columns=['区域', '商圈', '均价', '成交量'])
    DIST = get_dist_urls(URL)
    for d in DIST:
        print(f'正在收集{d}区数据，商圈如下')
        CBD = get_cbd_urls(DIST[d])
        for c in CBD:
            print(f'- {c}')
            p, q = get_info(CBD[c])
            info = pd.DataFrame([[d,c,p,q]], columns=['区域', '商圈', '均价', '成交量'])
            INFO = INFO.append(info)

    INFO.to_csv('soufang.csv', index=False, encoding='utf_8_sig')
    print('全部数据已收集')
    
    return True

main()
