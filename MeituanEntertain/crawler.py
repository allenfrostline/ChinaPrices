# -*- coding: utf-8 -*-

#################################### update ####################################
# 201707031616 增加了是否要求所有值均非空的输入，如果是的话就省掉一大部分清洗了
# 201707031410 由于美团手机版页面只能查看最多50页，现加入区域码
# 201707031005 对销量为空的服务进行了处理
# 201707022350 第一个版本

#################################### import ####################################
import json
# import random
import requests
import pandas as pd
# from time import sleep
from bs4 import BeautifulSoup
from header import random_header

#################################### config ####################################
COLUMNS = ['商家', '区域', '商圈', '星级', '服务', '价格', '销量']
INFO = pd.DataFrame(columns=COLUMNS)
EMPTY_ALLOW = False
BIDLIST = {}
CITY_LONG = {
             # '上海':'shanghai', '北京':'beijing', '广州':'guangzhou', '深圳':'shenzhen',
             '石家庄':'shijiazhuang', '大连':'dalian', '沈阳':'shenyang', '哈尔滨':'haerbin',
             '宁波':'ningbo','杭州':'hangzhou','厦门':'xiamen','泉州':'quanzhou',
             '福州':'fuzhou','青岛':'qingdao','济南':'jinan','佛山':'foshan',
             '珠海':'zhuhai','广州':'guangzhou','武汉':'wuhan','成都':'chengdu',
             '昆明':'kunming','南宁':'nanning','太原':'taiyuan','长春':'changchun','苏州':'suzhou',
             '南京':'nanjing','合肥':'hefei','南昌':'nanchang','郑州':'zhengzhou',
             '长沙':'changsha','海口':'haikou','贵阳':'guiyang','西安':'xian',
             '呼和浩特':'huhehaote','重庆':'chongqing','天津':'tianjin'
            }
SERVICE = {'按摩','足浴','理发','KTV'}

#################################### crawler ###################################
def get_proxy():
    return requests.get("http://127.0.0.1:5000/get/").text

def delete_proxy(proxy):
    requests.get("http://127.0.0.1:5000/delete/?proxy={}".format(proxy))

def request(url):
    while True:
        try:
            proxy = get_proxy()
            html = requests.get(url, timeout=10, headers=random_header(), proxies={'http':'http://{}'.format(proxy)}).text
            break
        except:
            print('代理失效:', proxy)
            delete_proxy(proxy)
    return html

def get_bidlist(city):
    url = 'http://i.meituan.com/s/{}-0'.format(city)
    html = request(url)
    soup = BeautifulSoup(html, 'html.parser')
    cont = json.loads(soup.select('div[id=filterData]')[0].get_text())['BizAreaList'][1:]
    BIDLIST = {item['id']:item['name'] for item in cont}
    return BIDLIST

def get_page(url, category, city_cn, bid):
    global COLUMNS
    global INFO
    global BIDLIST
    global CITY

    html = request(url)
    soup = BeautifulSoup(html, 'html.parser')

    noinfo = '为您推荐' in soup.text # 最后一页
    if noinfo:
        return False
    else:
    	urls = soup.select('dl[gaevent="search/list"]')

    for item in urls: # 一个item即一个商家
        provider = item.select('dd[class="poi-list-item"]')[0]
        shop = provider.select('span[class="poiname"]')[0].get_text()
        try: 
            star = provider.select('em[class="star-text"]')[0].get_text()
        except:
            continue
        dist = provider.select('p')[0].select('a')[0].get_text()

        product = item.select('dl[class="list"]')

        for prod in product: # 一个prod即该商家的一种服务
            name = prod.select('div[class="title text-block"]')[0].get_text()
            prce = prod.select('div[class="price"]')[0].select('span')[0].get_text()
            try: 
                quan = prod.select('a[class="statusInfo"]')[0].get_text()
            except:
                continue
            quan = quan[2:]

            # sleep(random.uniform(0,.5))
            info = [shop, BIDLIST[bid], dist, star, name, prce, quan]
            print('  ·',', '.join(info))
            INFO = INFO.append(pd.DataFrame([info], columns=COLUMNS))
    
    INFO.to_csv('二线/{}_{}.csv'.format(category, city_cn), index=False, encoding='utf_8_sig')
    return True

##################################### main #####################################
def main():
    global INFO
    global BIDLIST
    global CITY

    # CITY_CN = input('城市: ')
    CITY = CITY_LONG[CITY_CN]
    # CATEGORY = input('服务类别: ')z
    print('正在搜索 {} 的行政区'.format(CITY_CN))
    while True:
        try:
            BIDLIST = get_bidlist(CITY)
            break
        except:
            print('找不到行政区? 再来一遍')
            # sleep(random.uniform(0,.5))

    print('搜索完成，结果如下:', ', '.join(BIDLIST.values()))
    
    for bid in BIDLIST:
        print('正在搜索 {}{} 的 {}'.format(CITY_CN, BIDLIST[bid], CATEGORY))
        p = 1
        while True:
            url = 'http://i.meituan.com/s/{}-{}?bid={}&sid=solds&p={}'.format(CITY, CATEGORY, bid, p)
            if get_page(url, CATEGORY, CITY_CN, bid):
                print('- 第 {} 页已完成'.format(p))
                p += 1
            else:
                print('- {}{} 搜索完成'.format(CITY_CN, BIDLIST[bid]))
                break

    print('全部数据已收集')
    return True

for CATEGORY in SERVICE:
    for CITY_CN in CITY_LONG:
        INFO = pd.DataFrame(columns=COLUMNS)
        main()
