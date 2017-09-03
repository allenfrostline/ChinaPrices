#! encoding: utf-8

#################################### import ####################################
import re
import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver

#################################### config ####################################
SCROLL_PAUSE = 2
CATEGORY = [
            'chuancai',
            'yuegangcai',
            'jiangzhecai',
            'lucaibeijingcai',
            'xican',
            # 'huoguo',
           ]
COLUMNS = ['菜系分类', '商家名称', '下辖区', '商圈', '人均消费', '星级', '评价人数']
DISTRICT = [
            '浦东新区', '徐汇区', '长宁区', '黄浦区', '静安区', '闵行区',
	        '卢湾区', '杨浦区', '普陀区', '虹口区', '闸北区', '宝山区',
	        '松江区', '嘉定区', '金山区', '青浦区', '奉贤区', '崇明区',
           ]
INFO = pd.DataFrame(columns = COLUMNS)

#################################### crawler ###################################
def scroll_to_end(driver):
    last_height = driver.execute_script('return document.body.scrollHeight')
    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        sleep(SCROLL_PAUSE)
        new_height = driver.execute_script('return document.body.scrollHeight')
        if new_height == last_height:
            break
        else:
            last_height = new_height

def get_page(category, dist):
    global INFO
    page = 1
    url = 'http://sh.meituan.com/category/{}/all/rating'.format(category)
    ch_op = webdriver.ChromeOptions()
    proxy = "117.143.109.158:80" # IP:PORT or HOST:PORT
    # prefs = {"profile.managed_default_content_settings.images":2}
    ch_op.add_argument('--proxy-server=%s' % proxy)
    # ch_op.add_experimental_option("prefs",prefs)
    driver = webdriver.Chrome(chrome_options=ch_op)
    driver.set_page_load_timeout(50)
    driver.set_script_timeout(50)
    driver.get(url)
    sleep(SCROLL_PAUSE)
    # wait(driver, 50).until(lambda driver: driver.find_element_by_link_text('下一页'))
    driver.find_element_by_link_text(dist).click()
    while True:
        scroll_to_end(driver)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        shops = soup.findAll('div', {'class':re.compile('poi-tile-nodeal')})
        for shop in shops:
        	try:
        	    info = shop.select('div[class="poi-tile__info"]')[0]
        	    cat = category
        	    nam = info.select('a')[0].get_text()
        	    dst = dist
        	    cbd = info.select('div[class="tag-list"]')[0].select('a')[1].get_text()
        	    tmp = info.select('div[class="rate"]')[0]
        	    rat = tmp.select('span[class="rate-stars"]')[0].get('style')[6:]
        	    num = tmp.select('span[class="num"]')[0].get_text()
        
        	    money = shop.select('div[class="poi-tile__money"]')[0]
        	    avg = money.select('span[class="price"]')[0].get_text().replace('¥','')
        
        	    result = [cat, nam, dst, cbd, avg, rat, num]
        	    print('-', result)
        	    INFO = INFO.append(pd.DataFrame([result], columns=COLUMNS))
        	except:
        		print('- 出问题了?')
    
        INFO.to_csv('food1.csv', index=0, encoding='utf-8-sig')

        xml = BeautifulSoup(html, 'xml').get_text()
        if '下一页' in xml:
        	print('- 第 {} 页已完成'.format(page))
        	page += 1
        	driver.find_element_by_link_text('下一页').click()
        else: 
        	print('所以页面收集完成\n')
        	driver.quit()
        	return True

##################################### main #####################################
def main():
	global INFO
	for category in CATEGORY:
		for dist in DISTRICT:
			print('正在收集 {} 的 {}'.format(dist, category))
			get_page(category, dist)

if __name__ == '__main__':
	main()