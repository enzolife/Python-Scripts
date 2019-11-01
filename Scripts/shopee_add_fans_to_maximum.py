#!/usr/bin/env python
# coding: utf-8

# In[53]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import logging
import os
import datetime


# In[54]:


# 获取脚本的当前路径，避免计划执行时路径出错
home_dir = os.path.dirname(os.path.realpath(__file__))
# 更换workding directory
working_directory = home_dir
os.chdir(working_directory)


# In[55]:


logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')


# In[56]:


# 屏幕最大化，且指定下载目录
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

prefs = {"profile.default_content_settings.popups": 0,
         "directory_upgrade": True,
         "profile.default_content_setting_values.notifications" : 2}
options.add_experimental_option("prefs", prefs)


# In[57]:


# 使用chromedriver才可以用开发者权限
chrome_driver_path = ".//chrome_driver//chromedriver.exe"
browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)


# In[58]:


# main page
main_page_url = "http://shopee.sg"
browser.get(main_page_url)

# remove ads, refresh again
for i in range(5):
    browser.get(main_page_url)
    time.sleep(10)


# In[59]:


# login
LoginElem = browser.find_elements_by_css_selector('.navbar__link.navbar__link--account.navbar__link--tappable.navbar__link--hoverable.navbar__link-text.navbar__link-text--medium')
'''
有关Selenium Compound class names not permitted的错误
可以参考https://stackoverflow.com/questions/37771604/selenium-compound-class-names-not-permitted
使用css_selector解决即可
'''
# 点击登入，弹出账户密码输入框
LoginElem[1].click()
time.sleep(10)


# In[60]:


acc_password_input_elem = browser.find_elements_by_css_selector('._2QBp41._1b-IZR')
try:
    acc_password_input_elem[0].click()
    acc_password_input_elem[0].send_keys('tengus1.sg')
    acc_password_input_elem[1].click()
    acc_password_input_elem[1].send_keys('tengus1803')
except:
    time.sleep(30)
    acc_password_input_elem = browser.find_elements_by_css_selector('._2QBp41._1b-IZR')
    acc_password_input_elem[0].click()
    acc_password_input_elem[0].send_keys('tengus1.sg')
    acc_password_input_elem[1].click()
    acc_password_input_elem[1].send_keys('tengus1803')
time.sleep(10)


# In[61]:


Login_button_elem = browser.find_elements_by_css_selector('._2DvX7K._3j9-lD._3ddytl.SjORHu')
time.sleep(10)
Login_button_elem[0].click()
time.sleep(10)


# In[62]:


# change current tab size
# browser.set_window_size(400, 862)    


# In[63]:


# add fans from Top Seller's shop
top_shop_id = 11918
top_shop_url = 'https://shopee.sg/shop/' + str(top_shop_id) + '/followers/?__classic__=1'
browser.get(top_shop_url)


# In[64]:


# add certain number of fans
to_add_num_of_following = 400
num_of_following_display = len(browser.find_elements_by_css_selector('.clickable_area.middle-centered-div'))


# In[65]:


# page down until we get at least 400 fans to cancel
# while num_of_following_display <= 1000:
    # body = browser.find_element_by_css_selector('body')
    # body.send_keys(Keys.PAGE_DOWN)
    # body.send_keys(Keys.END)
    # time.sleep(5)
    # num_of_following_display = len(browser.find_elements_by_css_selector('.clickable_area.middle-centered-div'))
    
# num_of_following_display


# In[66]:


following_buttons = browser.find_elements_by_css_selector('.btn-follow.follow.L14')
# len(following_buttons)


# In[67]:


i = 0
total_add_num_of_following = to_add_num_of_following


# In[68]:


browser.find_element_by_css_selector('body').send_keys(Keys.CONTROL + Keys.HOME)


# In[69]:


while i <= total_add_num_of_following - 1:  
    while to_add_num_of_following > 0:
        if i + 1 > len(following_buttons):
            browser.find_element_by_css_selector('body').send_keys(Keys.PAGE_DOWN)
            time.sleep(10)
        
        following_buttons = browser.find_elements_by_css_selector('.btn-follow.follow.L14')
        logging.info('Now we have ' + str(len(following_buttons)) + ' following buttons on the screen.')
        logging.info('Now run the ' + str(i + 1) + ' time.')
        # if following_buttons[i].text == '+ 關注':
        # if following_buttons[i].text == '+ ติดตาม':
        if following_buttons[i].text == '+ Follow':
            # print(following_buttons[i].text)
            shopid = following_buttons[i].get_attribute('shopid')
            following_buttons[i].click()
            time.sleep(5)
            to_add_num_of_following -= 1
            logging.info(str(shopid) + ' is following now, ' + str(to_add_num_of_following) + ' following remains.')
        else:
            logging.warning('Skip this one. It\'s following already.')
        i += 1


# In[70]:


# 关闭
browser.quit()

