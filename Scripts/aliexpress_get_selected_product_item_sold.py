#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import os
import zipfile
import shutil
from datetime import date
import logging


# In[2]:


# 获取脚本的当前路径，避免计划执行时路径出错
home_dir = os.path.dirname(os.path.realpath(__file__))
# 更换workding directory
working_directory = home_dir
os.chdir(working_directory)


# In[3]:


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# In[4]:


# 屏幕最大化，且指定下载目录
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# 添加翻墙配置
# 参考 https://www.codetd.com/article/4692519
# options.add_argument('--proxy-server=socks5://127.0.0.1:1080')

prefs = {"profile.default_content_settings.popups": 0,
         # "download.default_directory": r"D:\Program Files (x86)\百度云同步盘\Dropbox\-E·J- 2014.5.1\2016.12.15 店小秘数据分析\\", # IMPORTANT - ENDING SLASH V IMPORTANT
         "directory_upgrade": True}
options.add_experimental_option("prefs", prefs)


# In[5]:


# 使用chromedriver才可以用开发者权限
chrome_driver_path = ".//chrome_driver//chromedriver.exe"
browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)


# In[6]:


# 重刷页面的脚本
def open_page(browser, page_url):
    i = 0
    while i == 0:
        try:
            # browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)
            browser.get(page_url)
            time.sleep(10)
            i = 1
        except:
            pass
        
# 刷新
def refresh_page(browser):
    i = 0
    while i == 0:
        try:
            # browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)
            browser.refresh()
            time.sleep(10)
            i = 1
        except:
            pass


# In[7]:


aliexpress_home_page = 'https://www.aliexpress.com/'

open_page(browser, aliexpress_home_page)

# remove ads, refresh again
for i in range(5):
    # browser.refresh()
    # time.sleep(10)
    refresh_page(browser)


# In[8]:


selected_item_id_list = [32597758635,
32942144691,
32810164959,
32632600938,
33002563321,
32810112786,
32888170029,
32788890848,
32880886831,
32874982263,
32959239179,
32850704130,
32959386419,
32788890852,
32993977479,
4000069793865,
32343136892,
32790959319,
32954653412,
32617572014,
32788932952,
32942053060,
32957115062,
32865455717,
32971072372,
33006223242,
33035020392,
32852427227,
32887697518,
33053088336,
4000223489312,
32862921368,
32992033664,
4000223461794,
32818464811,
33055562905,
32799435466,
32327844257,
32858191355,
32881314860,
32982582725,
32500831234,
32827720628,
32910850460,
32887647476,
32342515676,
32531261115,
32979767907,
33003521931,
32619544738,
32998526782,
32489626448,
32851896442,
32888118667,
33037121126,
33016171172,
32803469620
]


# In[9]:


# item_url = 'https://www.aliexpress.com/item/---/' + str(selected_item_id_list[0]) + '.html'
# item_url


# In[10]:


# browser.get(item_url)


# In[11]:


# item_sold = browser.find_elements_by_css_selector('.product-reviewer-sold')[0]
# item_sold.text


# In[12]:


result_df = pd.DataFrame()


# In[13]:


item_id_list, item_sold_list, item_name_list = list(), list(), list()


# In[ ]:


for item_id in selected_item_id_list:
    try:
        item_url = 'https://www.aliexpress.com/item/---/' + str(item_id) + '.html'
        open_page(browser, item_url)

        item_sold = browser.find_elements_by_css_selector('.product-reviewer-sold')[0].text
        item_name = browser.find_elements_by_css_selector('.product-title')[0].text

        item_id_list.append(item_id)
        item_sold_list.append(item_sold)
        item_name_list.append(item_name)

        logging.info(str(item_id) + ' has been finished.')
    except:
        logging.info(str(item_id) + ' has not been finished.')
    
result_df['item_id'] = item_id_list
result_df['item_sold'] = item_sold_list
result_df['item_name'] = item_name_list


# In[ ]:


today = date.today()
d1 = today.strftime("%Y-%m-%d")

result_df.to_csv('../aliexpress_selected_product_crawling/' + d1 + '.csv')
browser.quit()

