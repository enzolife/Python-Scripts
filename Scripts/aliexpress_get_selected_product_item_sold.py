
# coding: utf-8

# In[14]:

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import os
import zipfile
import shutil
from datetime import date
import logging


# In[ ]:

# 获取脚本的当前路径，避免计划执行时路径出错
home_dir = os.path.dirname(os.path.realpath(__file__))
# 更换workding directory
working_directory = home_dir
os.chdir(working_directory)


# In[15]:

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# In[16]:

# 屏幕最大化，且指定下载目录
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

prefs = {"profile.default_content_settings.popups": 0,
         # "download.default_directory": r"D:\Program Files (x86)\百度云同步盘\Dropbox\-E·J- 2014.5.1\2016.12.15 店小秘数据分析\\", # IMPORTANT - ENDING SLASH V IMPORTANT
         "directory_upgrade": True}
options.add_experimental_option("prefs", prefs)


# In[17]:

# 使用chromedriver才可以用开发者权限
chrome_driver_path = ".//chrome_driver//chromedriver.exe"
browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)


# In[18]:

browser.get('https://www.aliexpress.com/')
time.sleep(5)
browser.get('https://www.aliexpress.com/')
time.sleep(5)


# In[19]:

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
32803469620,
4000131355320,
33027410897,
32803617403,
32964185065,
32672034760,
33063807272,
4000052060355,
32678406564,
32889507635,
32810991774,
33018219380,
32821069855,
4000018022741,
33027414763,
32814894221,
33055874024,
1551834155,
32954995489,
4000087977155,
32839270065,
32606370302,
32739690304
]


# In[20]:

# item_url = 'https://www.aliexpress.com/item/---/' + str(selected_item_id_list[0]) + '.html'
# item_url


# In[21]:

# browser.get(item_url)


# In[22]:

# item_sold = browser.find_elements_by_css_selector('.product-reviewer-sold')[0]
# item_sold.text


# In[23]:

result_df = pd.DataFrame()


# In[24]:

item_id_list, item_sold_list, item_name_list = list(), list(), list()


# In[25]:

for item_id in selected_item_id_list:
    item_url = 'https://www.aliexpress.com/item/---/' + str(item_id) + '.html'
    browser.get(item_url)
    time.sleep(5)
    
    item_sold = browser.find_elements_by_css_selector('.product-reviewer-sold')[0].text
    item_name = browser.find_elements_by_css_selector('.product-title')[0].text
    
    item_id_list.append(item_id)
    item_sold_list.append(item_sold)
    item_name_list.append(item_name)
    
    logging.info(str(item_id) + ' has been finished.')
    
result_df['item_id'] = item_id_list
result_df['item_sold'] = item_sold_list
result_df['item_name'] = item_name_list


# In[26]:

today = date.today()
d1 = today.strftime("%Y-%m-%d")

result_df.to_csv('../aliexpress_selected_product_crawling/' + d1 + '.csv')
browser.quit()

