
# coding: utf-8

# In[43]:

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import datetime
import logging
import os

import random


# In[44]:

# Date
today_date = datetime.date.today() + datetime.timedelta(days=0)
yesterday_date = datetime.date.today() + datetime.timedelta(days=-1)
seven_days_before_date = datetime.date.today() + datetime.timedelta(days=-7)

today_date_string = today_date.strftime('%Y_%m_%d')


# In[45]:

log_file_name = 'shopee_add_and_cancel_fans_log\\shopee_add_and_cancel_fans_log_' + today_date_string + '.txt'

# logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# In[46]:

# 屏幕最大化，且指定下载目录
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

prefs = {"profile.default_content_settings.popups": 0,
         "directory_upgrade": True}
options.add_experimental_option("prefs", prefs)


# In[47]:

# 使用chromedriver才可以用开发者权限
chrome_driver_path = "D://Program Files (x86)//百度云同步盘//我的软件//chromedriver.exe"
# browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)


# In[48]:

# 所需参数
# 站点；站点后缀；账户；密码；站点top卖家shopid；top卖家username（方便识别）
shop_list = [['tw', 'tw', 23070969, 'poweradapter.tw', 'kuangyiqiao1991', 9469128, 'alonso.tw'],
             ['tw', 'tw', 25482220, 'tengus.tw', 'tengus1803', 23068230, 'iu.tw'],
             ['tw', 'tw', 58707738, 'qianjiaozi', 'qianjiaozi888', 26513957, 'beibei.tw'],
             ['tw', 'tw', 66377809, 'qianjiaozi1', 'qianjiaozi888', 23068230, 'iu.tw'],
             ['tw', 'tw', 62416366, 'tengus1.tw', 'tengus1803', 23068230, 'iu.tw'],
             ['tw', 'tw', 62416544, 'tengus2.tw', 'tengus1803', 23068230, 'iu.tw'],
             ['tw', 'tw', 63534861, 'qianjiaozitw1', 'tengus1803', 23068230, 'iu.tw'],
             ['tw', 'tw', 62887142, 'yilanlu.tw', 'yilanlu888', 23481977, 'huoyi.tw'],
             ['my', 'com.my', 53580963, 'qianjiaozi.my', 'tengus1803', 10891137, 'winners.my'],
             ['my', 'com.my', 59848325, 'tengus.my', 'tengus1803', 10891137, 'winners.my'],
             ['my', 'com.my', 62418141, 'tengus1.my', 'tengus1803', 10891137, 'winners.my'],
             ['my', 'com.my', 62418493, 'tengus2.my', 'tengus1803', 10891137, 'winners.my'],
             ['id', 'co.id', 59846508, 'tengus.id', 'tengus1803', 28135012, 'sunnyfun.id'],
             ['id', 'co.id', 62417386, 'tengus1.id', 'tengus1803', 28135012, 'sunnyfun.id'],
             ['id', 'co.id', 62417551, 'tengus2.id', 'tengus1803', 28135012, 'sunnyfun.id']
            ]


# In[49]:

# 转换为dataframe
shop_df_columns = ['site', 'site_suffix', 'shopid', 'acc', 'pwd', 'top_shop_id', 'top_shop_username']
shop_df = pd.DataFrame(shop_list, columns=shop_df_columns)


# In[50]:

# 商品置顶函数
def boost_product(site, site_suffix, shopid, acc, pwd):
    # 打开浏览器
    logging.info('Open the browser.')
    browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)
    
    # main page
    main_page_url = "http://shopee." + site_suffix
    browser.get(main_page_url)
    time.sleep(10)
    
    # remove ads, refresh again
    browser.get(main_page_url)
    time.sleep(10)

    # if the shop is on my site, should press the button to choose language
    if site == 'my':
        language_selector = browser.find_elements_by_css_selector('.shopee-button-outline.shopee-button-outline--primary-reverse')
        language_selector[2].click()
        logging.info('Choose Chinese as language.')
        time.sleep(10)
    
    # login
    logging.info('Start to login.')
    LoginElem = browser.find_elements_by_css_selector('.navbar__link.navbar__link--account.navbar__link--tappable.navbar__link--hoverable.navbar__link-text.navbar__link-text--medium')
    
    # 点击登入，弹出账户密码输入框
    LoginElem[1].click()
    time.sleep(10)
    
    # 输入
    acc_password_input_elem = browser.find_elements_by_css_selector('.input-with-status__input')
    try:
        acc_password_input_elem[0].click()
        acc_password_input_elem[0].send_keys(acc)
        acc_password_input_elem[1].click()
        acc_password_input_elem[1].send_keys(pwd)
    except:
        time.sleep(30)
        acc_password_input_elem = browser.find_elements_by_css_selector('.input-with-status__input')
        acc_password_input_elem[0].click()
        acc_password_input_elem[0].send_keys(acc)
        acc_password_input_elem[1].click()
        acc_password_input_elem[1].send_keys(pwd)
    time.sleep(10)
    
    # 点击提交
    Login_button_elem = browser.find_elements_by_css_selector('.shopee-button-solid.shopee-button-solid--primary')
    Login_button_elem[0].click()
    time.sleep(10)
    
    # switch to my seller center
    logging.info('Switch to my seller center.')
    seller_center_main_page = 'https://seller.shopee.' + site_suffix
    browser.get(seller_center_main_page)
    time.sleep(10)
    
    # my products page
    logging.info('Switch to my products page')
    my_products = browser.find_elements_by_css_selector('.home-big-button__title')
    my_products[0].click()
    time.sleep(10)
    
    # product boost
    try:
        my_products_boost = browser.find_elements_by_css_selector('.shopee-button.shopee-button--inactive.shopee-button--frameless.shopee-button--medium.ember-view')
        # random select 5 products to boost
        random_num_list = random.sample(range(0, len(my_products_boost)-1), 5)
        for index, random_num in enumerate(random_num_list):
            my_products_boost[random_num].click()
            logging.info('Boost ' + str(index) + ' product.')
        logging.info('Product Boost is completed.')
    except:
        pass
    
    # 关闭
    browser.quit()


# In[51]:

# 历遍所有shop
for index, my_shop in shop_df.iterrows():
    site = my_shop[0]
    site_suffix = my_shop[1]
    shopid = my_shop[2]
    acc = my_shop[3]
    pwd = my_shop[4]
    
    # 执行
    try:
        logging.info('Now it\'s running the script on ' + acc + '.')
        boost_product(site, site_suffix, shopid, acc, pwd)
        logging.info('Finished running the script on ' + acc + '.')
    except Exception as err:
        logging.info('An exception occurred: ' + str(err) + '.')

