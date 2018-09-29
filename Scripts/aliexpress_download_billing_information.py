
# coding: utf-8

# In[6]:

from selenium import webdriver
import pandas as pd
import time
import datetime
import os


# In[7]:

default_directory = r"D:\Program Files (x86)\百度云同步盘\Dropbox\-E·J- 2014.5.1\2016.12.15 店小秘数据分析\2018.9.7 aliexpress放款记录\\"
# default_directory = r"D:\\"


# In[8]:

# 屏幕最大化
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

prefs = {"profile.default_content_settings.popups": 0,
         "download.default_directory": default_directory, # IMPORTANT - ENDING SLASH V IMPORTANT
         "directory_upgrade": True}
options.add_experimental_option("prefs", prefs)


# In[9]:

cwd = os.path.abspath(".")
cwd = os.path.dirname(os.path.abspath("__file__"))
# print(cwd)


# In[10]:

# 使用chromedriver才可以用开发者权限
chrome_driver_path = os.path.join(cwd, "chrome_driver", "chromedriver.exe")
chrome_driver_path = "C:\\Users\kuang\Documents\Python-Scripts\Scripts\chrome_driver\chromedriver.exe" 
browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)


# In[11]:

browser.get('https://fund.aliexpress.com/fundQueryManage.htm?spm=a2g0s.9042311.0.0.6f654c4dUIQvVb')


# In[ ]:

# 切换到输入密码的iframe
browser.switch_to.frame('alibaba-login-box')


# In[ ]:

acc_password_class = ".fm-text"
acc_password_input_elem = browser.find_elements_by_css_selector(acc_password_class)
# len(acc_password_input_elem)


# In[ ]:

# 输入账户密码登录
acc_password_input_elem[0].click()
acc_password_input_elem[0].send_keys('15622252963@163.com')
acc_password_input_elem[1].click()
acc_password_input_elem[1].send_keys('932584162apple')
time.sleep(10)


# In[ ]:

# 点击登录
log_in_button = browser.find_element_by_css_selector('.fm-button.fm-submit')
# type(log_in_button)


# In[ ]:

log_in_button.click()
time.sleep(10)


# In[ ]:

# 点击订单记录
browser.find_elements_by_css_selector('.ui-switchable-trigger')[2].click()


# In[ ]:

# 点击导出
browser.find_element_by_id('fundOrderExport').click()
time.sleep(10)


# In[ ]:

# 下载csv
browser.find_element_by_partial_link_text('.csv').click()
time.sleep(60)


# In[ ]:

# 关闭浏览器
browser.quit()

