#!/usr/bin/env python
# coding: utf-8

# In[10]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import os
import zipfile
import shutil
from datetime import date


# In[11]:


# 获取脚本的当前路径，避免计划执行时路径出错
home_dir = os.path.dirname(os.path.realpath(__file__))
# 更换workding directory
working_directory = home_dir
os.chdir(working_directory)


# In[12]:


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


# In[13]:


# 使用chromedriver才可以用开发者权限
chrome_driver_path = ".//chrome_driver//chromedriver.exe"
browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)


# In[14]:


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


# In[15]:


aliexpress_home_page = 'https://www.aliexpress.com/'

open_page(browser, aliexpress_home_page)

# remove ads, refresh again
for i in range(5):
    # browser.refresh()
    # time.sleep(10)
    refresh_page(browser)


# In[16]:


# 点击搜索框
search_box = browser.find_elements_by_css_selector('.search-key')[0]
search_box.click()
search_box.send_keys('universal laptop charger')
time.sleep(5)


# In[17]:


# 点击搜索
search_button = browser.find_elements_by_css_selector('.search-button')[0]
search_button.click()
time.sleep(5)


# In[18]:


# 翻页到最后
body = browser.find_element_by_css_selector('body')
for i in range(30):
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(2)
body.send_keys(Keys.END)
time.sleep(10)


# In[19]:


# 查找商品
item_price = browser.find_elements_by_css_selector('.price-current')
item_title = browser.find_elements_by_css_selector('.item-title')
item_sold = browser.find_elements_by_css_selector('.sale-value-link')
store_name = browser.find_elements_by_css_selector('.store-name')
# print(len(item_price))
# print(len(item_title))
# print(len(item_sold))
# print(len(store_name))


# In[20]:


result_df = pd.DataFrame()
# result_df


# In[21]:


item_price_list, item_title_list, item_sold_list, store_name_list, store_url_list, item_url_list = list(), list(), list(), list(), list(), list()

for i in range(len(item_sold)):
    item_price_list.append(item_price[i].text)
    item_title_list.append(item_title[i].text)
    item_sold_list.append(item_sold[i].text)
    store_name_list.append(store_name[i].text)
    store_url_list.append(store_name[i].get_attribute("href"))
    item_url_list.append(item_title[i].get_attribute("href"))
    
result_df['item_price'] = item_price_list
result_df['item_title'] = item_title_list
result_df['item_sold'] = item_sold_list
result_df['store_name'] = store_name_list
result_df['store_url'] = store_url_list
result_df['item_url'] = item_url_list
result_df['rank'] = result_df.index + 1
# result_df


# In[22]:


today = date.today()
d1 = today.strftime("%Y-%m-%d")

result_df.to_csv('../aliexpress_product_ranking/' + d1 + '.csv')
browser.quit()

