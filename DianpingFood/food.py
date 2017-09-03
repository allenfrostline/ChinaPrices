# -*- coding: utf-8 -*-

#################################### import ####################################
import re
import requests
import random
import pandas as pd
# from time import sleep
from bs4 import BeautifulSoup
from header import random_header

#################################### config ####################################
random.seed(123)
COLUMNS = ['菜系分类', '商家名称', '下辖区', '商圈', '人均消费', '星级', '评价人数']
INFO = pd.DataFrame(columns=COLUMNS)
IP_LIST = []

#################################### crawler ###################################
def get_proxy():
    return requests.get("http://127.0.0.1:5000/get/").text

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5000/delete/?proxy={}".format(proxy))

def get_soup(url, parser):
    while True:
    	try:
        	proxy = get_proxy()
        	html = requests.get(url, timeout=5, headers=random_header(), proxies={'http':'http://{}'.format(proxy)}).text
        	break
    	except:
        	print('代理失效:', proxy)
        	delete_proxy(proxy)
    return BeautifulSoup(html, parser)

def get_group(soup):
    group = soup.select('div[id="classfy"]')[0].select('a')
    GROUP = {}
    for c in group:
        tmp = c.get('href').split('/')[-1]
        # print(tmp)
        index = re.findall(r'g\d+(?=o)', tmp)[0]
        # print(index)
        name = c.get_text()
        GROUP[index] = name
    return GROUP

def get_bidlist(soup):
    bidlist = soup.select('div[id="region-nav"]')[0].select('a')
    BIDLIST = {}
    for r in bidlist:
        tmp = r.get('href').split('/')[-1]
        # print(tmp)
        index = re.findall(r'[rc]\d+(?=o)', tmp)[0]
        # print(index)
        name = r.get_text()
        BIDLIST[index] = name
    return BIDLIST

##################################### main ####################################
def main():
    global INFO
    global IP_LIST

    soup = get_soup(URL.format('',''), 'lxml')
    # print(soup)
    while True:
        try:
            GROUP = get_group(soup)
            break
        except Exception as e:
            soup = get_soup(URL.format('',''), 'lxml')
            print('找不到菜系? 再来一遍')
            # print(e)
            # sleep(random.uniform(0,.5))
    
    print(f'正在搜索 {CITY} 的行政区')
    while True:
        try:
            BIDLIST = get_bidlist(soup)
            break
        except:
            soup = get_soup(URL.format('',''), 'lxml')
            print('找不到行政区? 再来一遍')
            # sleep(random.uniform(0,.5))
    print('搜索完成，结果如下:', ', '.join(BIDLIST.values()))
    for bid in BIDLIST:
        for g in GROUP:
            print('正在爬取 {} 的 {}'.format(BIDLIST[bid], GROUP[g]))
            theurl = URL.format(g,bid)
            url = theurl
            p = 1
            while True:
                for i in range(10):
                    try:
                        soup = get_soup(url, 'lxml')
                        shoplist = soup.select('div[class="shop-list J_shop-list shop-all-list"]')[0].select('li')
                        succ = 1
                        break
                    except:
                        # sleep(random.uniform(0,.5))
                        succ = 0
                if succ==0: 
                    print('{} 的 {} 返回为空'.format(BIDLIST[bid], GROUP[g]))
                    break
                for shop in shoplist:
                    try:
                        name = shop.select('div[class="tit"]')[0].select('a')[0].select('h4')[0].get_text()
                        cmmt = shop.select('div[class="comment"]')[0]
                        star = cmmt.select('span')[0].get('title')
                        rvew = cmmt.select('a[class="review-num"]')[0].select('b')[0].get_text()
                        mean = cmmt.select('a[class="mean-price"]')[0].select('b')[0].get_text()[1:]
                        cbd  = shop.select('div[class="tag-addr"]')[0].select('span[class="tag"]')[1].get_text()
                        info = [GROUP[g], name, BIDLIST[bid], cbd, mean, star, rvew]
                        INFO = INFO.append(pd.DataFrame([info], columns=COLUMNS))
                        print('  ·', ', '.join(info))
                    except:
                        if len(name):
                            print('# ·', name, '数据缺失')
                        else: 
                            print('# · 未知错误')
                # print(url)
                print('- 第 {} 页已完成'.format(p))
                if '下一页' in soup.text:
                    p += 1
                    url = theurl + 'p{}'.format(p)
                else:
                    print('- 全部页面已完成\n')
                    break

                INFO.to_csv('餐饮_{}.csv'.format(CITY), index=0, encoding='utf-8-sig')

CITY_INDEX = {
			  # '上海': '1',     '北京': '2',   '广州': '4',   '深圳': '7', 
              # '石家庄': '24',  '大连': '19',  '沈阳': '18',  '哈尔滨': '79', 
              # '宁波': '11',    '杭州': '3',   '厦门': '15',  '泉州': '129', 
              # '福州': '14',    '青岛': '21',  '济南': '22',  '佛山': '208', 
              # '珠海': '206',   '武汉': '16',  '成都': '8',   '昆明': '267', 
              # '南宁': '224',   '太原': '35',  '长春': '70',  '苏州': '6', 
              # '南京': '5',     '合肥': '110', '南昌': '134', '郑州': '160', 
              '长沙': '344',   '海口': '23',  '贵阳': '258', '西安': '17', 
              '呼和浩特': '46', '重庆': '9',   '天津': '10',
		     }
for CITY in CITY_INDEX:
    INFO = pd.DataFrame(columns=COLUMNS)
    URL = 'http://www.dianping.com/search/category/' + CITY_INDEX[CITY] + '/10/{}{}o3'
    main()
