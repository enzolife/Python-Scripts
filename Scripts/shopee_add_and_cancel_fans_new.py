#!/usr/bin/env python
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import datetime
import logging
import os


# In[2]:


# 获取脚本的当前路径，避免计划执行时路径出错
home_dir = os.path.dirname(os.path.realpath(__file__))
# 更换workding directory
working_directory = home_dir
os.chdir(working_directory)


# In[3]:


# pip install selenium


# In[4]:


# Date
today_date = datetime.date.today() + datetime.timedelta(days=0)
yesterday_date = datetime.date.today() + datetime.timedelta(days=-1)
seven_days_before_date = datetime.date.today() + datetime.timedelta(days=-7)

today_date_string = today_date.strftime('%Y_%m_%d')


# In[5]:


# os.getcwd()


# In[6]:


log_file_name = 'shopee_add_and_cancel_fans_log\\shopee_add_and_cancel_fans_log_' + today_date_string + '.txt'

# logging.basicConfig(filename=log_file_name, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# In[7]:


# 屏幕最大化，且指定下载目录
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# 添加翻墙配置
# 参考 https://www.codetd.com/article/4692519
options.add_argument('--proxy-server=socks5://127.0.0.1:1080')

prefs = {"profile.default_content_settings.popups": 0,
         "directory_upgrade": True,
         "profile.default_content_setting_values.notifications" : 2}
options.add_experimental_option("prefs", prefs)


# In[8]:


# 使用chromedriver才可以用开发者权限
chrome_driver_path = ".//chrome_driver//chromedriver.exe"
# browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)


# In[9]:


# 所需参数
# 站点；站点后缀；账户；密码；站点top卖家shopid；top卖家username（方便识别）
# shop_list = [['tw', 'tw', 23070969, 'poweradapter.tw', 'kuangyiqiao1991', 9469128, 'alonso.tw'],
#              ['tw', 'tw', 25482220, 'tengus.tw', 'tengus1803', 23068230, 'iu.tw'],
#              ['tw', 'tw', 58707738, 'qianjiaozi', 'qianjiaozi888', 26513957, 'beibei.tw'],
#              ['tw', 'tw', 66377809, 'qianjiaozi1', 'qianjiaozi888', 23068230, 'iu.tw'],
#              ['tw', 'tw', 62416366, 'tengus1.tw', 'tengus1803', 23068230, 'iu.tw'],
#              ['tw', 'tw', 62416544, 'tengus2.tw', 'tengus1803', 23068230, 'iu.tw'],
#              ['tw', 'tw', 63534861, 'qianjiaozitw1', 'tengus1803', 23068230, 'iu.tw'],
#              ['tw', 'tw', 62887142, 'yilanlu.tw', 'yilanlu888', 23481977, 'huoyi.tw'],
#              ['my', 'com.my', 53580963, 'qianjiaozi.my', 'tengus1803', 10891137, 'winners.my'],
#              ['my', 'com.my', 59848325, 'tengus.my', 'tengus1803', 10891137, 'winners.my'],
#              ['my', 'com.my', 62418141, 'tengus1.my', 'tengus1803', 10891137, 'winners.my'],
#              ['my', 'com.my', 62418493, 'tengus2.my', 'tengus1803', 10891137, 'winners.my'],
#              ['id', 'co.id', 59846508, 'tengus.id', 'tengus1803', 145423, 'Shopee Mamak],
#              ['id', 'co.id', 62417386, 'tengus1.id', 'tengus1803', 28135012, 'sunnyfun.id'],
#              ['id', 'co.id', 62417551, 'tengus2.id', 'tengus1803', 28135012, 'sunnyfun.id']]

# shop_list = [['tw', 'tw', 23070969, 'poweradapter.tw', 'kuangyiqiao1991', 9469128, 'alonso.tw'],
#              ['th', 'co.th', 117213614, 'tengus.th', 'tengus1803', 25926687, 'xiaozhainv']]

# shop_list = [['th', 'co.th', 117213614, 'tengus.th', 'tengus1803', 25926687, 'xiaozhainv'],
#              ['tw', 'tw', 23070969, 'poweradapter.tw', 'kuangyiqiao1991', 9469128, 'alonso.tw'],
#              ['sg', 'sg', 182539921, 'tengus1.sg', 'tengus1803', 11918, 'shopeesg'],
#              ['ph', 'ph', 182539050, 'tengus.ph', 'tengus1803', 2215148, 'YAZI FASHION ACCESSORIES INC.'],
#              ['id', 'co.id', 59846508, 'tengus.id', 'tengus1803', 11184349, 'Shopee Mamak']]


shop_list = [['th', 'co.th', 117213614, 'tengus.th', 'tengus1803', 25926687, 'xiaozhainv'],
             ['tw', 'tw', 23070969, 'poweradapter.tw', 'kuangyiqiao1991', 9469128, 'alonso.tw'],
             ['sg', 'sg', 182539921, 'tengus1.sg', 'tengus1803', 11918, 'shopeesg'],
             ['ph', 'ph', 182539050, 'tengus.ph', 'tengus1803', 2215148, 'YAZI FASHION ACCESSORIES INC.'],
             ['my', 'com.my', 59846508, 'tengus2.my', 'tengus1803', 145423, 'Shopee Mamak']]

# shop_list = [['th', 'co.th', 117213614, 'tengus.th', 'tengus1803', 25926687, 'xiaozhainv'],
#              ['tw', 'tw', 23070969, 'poweradapter.tw', 'kuangyiqiao1991', 9469128, 'alonso.tw']]

# shop_list = [['th', 'co.th', 117213614, 'tengus.th', 'tengus1803', 25926687, 'xiaozhainv']]

# shop_list = [['sg', 'sg', 182539921, 'tengus1.sg', 'tengus1803', 11918, 'shopeesg']]
# shop_list = [['ph', 'ph', 182539050, 'tengus.ph', 'tengus1803', 3256461, 'YAZI FASHION ACCESSORIES INC.']]


# In[10]:


# 转换为dataframe
shop_df_columns = ['site', 'site_suffix', 'shopid', 'acc', 'pwd', 'top_shop_id', 'top_shop_username']
shop_df = pd.DataFrame(shop_list, columns=shop_df_columns)


# In[11]:


# 关注及关注中多语言
following_language = ['关注中', '關注中', 'Following', 'Mengikuti', 'กำลังติดตาม']
not_following_language = ['+ 关注', '+ 關注', '+ Follow', '+ Ikuti', "+ ติดตาม"]


# In[12]:


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


# In[13]:


# 取关后关注函数
def add_and_cancel_fans(site, site_suffix, shopid, acc, pwd, top_shop_id, top_shop_username):
    # 打开浏览器
    logging.info('Open the browser.')
    browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)
    
    # main page
    main_page_url = "http://shopee." + site_suffix
    # browser.get(main_page_url)
    # time.sleep(10)
    open_page(browser, main_page_url)
    
    # remove ads, refresh again
    for i in range(5):
        # browser.refresh()
        # time.sleep(10)
        refresh_page(browser)

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
    acc_password_input_elem = browser.find_elements_by_css_selector('._3Ojta0._2A9mXk')
    try:
        acc_password_input_elem[0].click()
        acc_password_input_elem[0].send_keys(acc)
        acc_password_input_elem[1].click()
        acc_password_input_elem[1].send_keys(pwd)
    except:
        time.sleep(30)
        acc_password_input_elem = browser.find_elements_by_css_selector('._3Ojta0._2A9mXk')
        acc_password_input_elem[0].click()
        acc_password_input_elem[0].send_keys(acc)
        acc_password_input_elem[1].click()
        acc_password_input_elem[1].send_keys(pwd)
    time.sleep(10)
    
    # 点击提交
    Login_button_elem = browser.find_elements_by_css_selector('._1BMmPI._37G57D._7h_6kj._1qIIqG._3JP5il')
    Login_button_elem[0].click()
    logging.info('Login completed.')
    time.sleep(10)
    
    # switch to my following list
    logging.info('Switch to my following list.')
    my_fans_list_page = 'https://shopee.' + site_suffix + '/shop/' + str(shopid) + '/following/?__classic__=1'
    # browser.get(my_fans_list_page)
    open_page(browser, my_fans_list_page)
    
    # cancel certain number of following fans
    to_cancel_num_of_following = 400
    num_of_following_display = len(browser.find_elements_by_css_selector('.clickable_area.middle-centered-div'))
    
    # in case the following number is not greater than 500
    max_roll_time = 100
    roll_time = 0
    
    # page down until we get at least 500 fans to cancel
    while num_of_following_display <= 500 and roll_time <= max_roll_time:
        body = browser.find_element_by_css_selector('body')
        body.send_keys(Keys.END)
        time.sleep(2)
        num_of_following_display = len(browser.find_elements_by_css_selector('.clickable_area.middle-centered-div'))
        logging.info(str(num_of_following_display) + ' following on the list.')
        roll_time += 1
        logging.info('Roll the page for ' + str(roll_time) + ' time.')
    following_buttons = browser.find_elements_by_css_selector('.btn-follow.active.follow.L14')
    
    # actual following to cancel
    to_cancel_num_of_following = min(num_of_following_display, to_cancel_num_of_following)
    
    # page up to the top
    scroll_to_the_top = browser.find_element_by_css_selector('body').send_keys(Keys.CONTROL + Keys.HOME)
    time.sleep(5)
    scroll_to_the_top = browser.find_element_by_css_selector('body').send_keys(Keys.CONTROL + Keys.HOME)
    
    # start to cancel following
    logging.info('Start to cancel following.')
    i = 0
    total_cancel_num_of_following = to_cancel_num_of_following
    while i <= total_cancel_num_of_following - 1:
        while to_cancel_num_of_following > 0:
            logging.info('Now run the ' + str(i + 1) + ' time.')
            if following_buttons[i].text in following_language:
                buyer_shopid = following_buttons[i].get_attribute('shopid')
                following_buttons[i].click()
                time.sleep(1)
                to_cancel_num_of_following -= 1
                i += 1
                logging.info(acc + ': ' + str(buyer_shopid) + ' is not following now, ' + str(to_cancel_num_of_following) + ' following remains.')
    
    # add fans from Top Seller's followers
    logging.info('Switch to top seller follower page.')
    top_shop_url = 'https://shopee.' + site_suffix + '/shop/' + str(top_shop_id) + '/followers/?__classic__=1'
    open_page(browser, top_shop_url)
    
    # add certain number of fans
    to_add_num_of_following = 400
    num_of_following_display = len(browser.find_elements_by_css_selector('.clickable_area.middle-centered-div'))
    
    # page down until we get at least 400 fans to cancel
    logging.info('Start to roll down.')
    while num_of_following_display <= 1000:
        body = browser.find_element_by_css_selector('body')
        # body.send_keys(Keys.PAGE_DOWN)
        body.send_keys(Keys.END)
        time.sleep(2)
        num_of_following_display = len(browser.find_elements_by_css_selector('.clickable_area.middle-centered-div'))
    following_buttons = browser.find_elements_by_css_selector('.btn-follow.follow.L14')
    
    # start to follow buyers from top shop
    logging.info('Start to follow buyers.')
    i = 0
    total_add_num_of_following = to_add_num_of_following
    scroll_to_the_top = browser.find_element_by_css_selector('body').send_keys(Keys.CONTROL + Keys.HOME)

    while i <= total_add_num_of_following - 1:  
        while to_add_num_of_following > 0:
            logging.info('Now run the ' + str(i + 1) + ' time.')
            if following_buttons[i].text in not_following_language:
                # print(following_buttons[i].text)
                buyer_shopid = following_buttons[i].get_attribute('shopid')
                following_buttons[i].click()
                time.sleep(1)
                to_add_num_of_following -= 1
                logging.info(acc + ': ' + str(buyer_shopid) + ' is following now, ' + str(to_add_num_of_following) + ' following remains.')
            else:
                logging.info('Skip this one. It\'s following already.')
            i += 1    
    
    # 关闭
    browser.quit()


# In[14]:


# 历遍所有shop
for index, my_shop in shop_df.iterrows():
    site = my_shop[0]
    site_suffix = my_shop[1]
    shopid = my_shop[2]
    acc = my_shop[3]
    pwd = my_shop[4]
    top_shop_id = my_shop[5]
    top_shop_username = my_shop[6]
    
    # 执行
    try:
        logging.info('Now it\'s running the script on ' + acc + '.')
        add_and_cancel_fans(site, site_suffix, shopid, acc, pwd, top_shop_id, top_shop_username)
        logging.info('Finished running the script on ' + acc + '.')
    except Exception as err:
        logging.info('An exception occurred: ' + str(err) + '.')


# In[15]:


# browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)


# In[16]:


# browser.get('https://shopee.com.my')


# In[17]:


# language_selector = browser.find_elements_by_css_selector('.shopee-button-outline.shopee-button-outline--primary-reverse')
# len(language_selector)


# In[18]:


#language_selector[2].click()

