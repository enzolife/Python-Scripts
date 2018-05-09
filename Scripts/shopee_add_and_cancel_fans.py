
# coding: utf-8

# In[1]:

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time


# In[2]:

# 屏幕最大化，且指定下载目录
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

prefs = {"profile.default_content_settings.popups": 0,
         "directory_upgrade": True}
options.add_experimental_option("prefs", prefs)


# In[3]:

# 使用chromedriver才可以用开发者权限
chrome_driver_path = "D://Program Files (x86)//百度云同步盘//我的软件//chromedriver.exe"
browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)


# In[4]:

# main page
main_page_url = "http://shopee.co.id"
browser.get(main_page_url)

# remove ads, refresh again
browser.get(main_page_url)
time.sleep(10)


# In[5]:

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


# In[6]:

acc_password_input_elem = browser.find_elements_by_css_selector('.input-with-status__input')
try:
    acc_password_input_elem[0].click()
    acc_password_input_elem[0].send_keys('tengus.id')
    acc_password_input_elem[1].click()
    acc_password_input_elem[1].send_keys('tengus1803')
except:
    time.sleep(30)
    acc_password_input_elem = browser.find_elements_by_css_selector('.input-with-status__input')
    acc_password_input_elem[0].click()
    acc_password_input_elem[0].send_keys('tengus.id')
    acc_password_input_elem[1].click()
    acc_password_input_elem[1].send_keys('tengus1803')
time.sleep(10)


# In[7]:

Login_button_elem = browser.find_elements_by_css_selector('.shopee-button-solid.shopee-button-solid--primary')
time.sleep(10)
Login_button_elem[0].click()


# In[9]:

# change current tab size
# browser.set_window_size(400, 862)    


# In[10]:

# switch to my fans list
my_fans_list_page = 'https://shopee.co.id/shop/59846508/following/?__classic__=1'
browser.get(my_fans_list_page)


# In[11]:

# cancel certain number of following fans
to_cancel_num_of_following = 400
num_of_following_display = len(browser.find_elements_by_css_selector('.clickable_area.middle-centered-div'))

# page down until we get at least 400 fans to cancel
while num_of_following_display <= 500:
    body = browser.find_element_by_css_selector('body')
    body.send_keys(Keys.PAGE_DOWN)
    time.sleep(5)
    num_of_following_display = len(browser.find_elements_by_css_selector('.clickable_area.middle-centered-div'))


# In[12]:

following_buttons = browser.find_elements_by_css_selector('.btn-follow.active.follow.L14')


# In[13]:

browser.maximize_window()
time.sleep(5)

# page up to the top
scroll_to_the_top = browser.find_element_by_css_selector('body').send_keys(Keys.CONTROL + Keys.HOME)


# In[14]:

i = 0
total_cancel_num_of_following = to_cancel_num_of_following
while i <= total_cancel_num_of_following - 1:
    while to_cancel_num_of_following > 0:
        print('Now run the ' + str(i + 1) + ' time.')
        if following_buttons[i].text == '关注中':
            shopid = following_buttons[i].get_attribute('shopid')
            following_buttons[i].click()
            time.sleep(5)
            to_cancel_num_of_following -= 1
            i += 1
            print(str(shopid) + ' is not following now, ' + str(to_cancel_num_of_following) + ' following remains.')


# In[14]:

# add fans from Top Seller's shop
top_shop_url = 'https://shopee.co.id/shop/13484023/followers/?__classic__=1'
browser.get(top_shop_url)


# In[15]:

# add certain number of fans
to_add_num_of_following = 400
num_of_following_display = len(browser.find_elements_by_css_selector('.clickable_area.middle-centered-div'))


# In[17]:

# page down until we get at least 400 fans to cancel
while num_of_following_display <= 1000:
    body = browser.find_element_by_css_selector('body')
    # body.send_keys(Keys.PAGE_DOWN)
    body.send_keys(Keys.END)
    time.sleep(5)
    num_of_following_display = len(browser.find_elements_by_css_selector('.clickable_area.middle-centered-div'))
    
num_of_following_display


# In[18]:

following_buttons = browser.find_elements_by_css_selector('.btn-follow.follow.L14')
len(following_buttons)


# In[23]:

i = 0
total_add_num_of_following = to_add_num_of_following

scroll_to_the_top = browser.find_element_by_css_selector('body').send_keys(Keys.CONTROL + Keys.HOME)

while i <= total_add_num_of_following - 1:  
    while to_add_num_of_following > 0:
        print('Now run the ' + str(i + 1) + ' time.')
        if following_buttons[i].text == '+ 关注':
            # print(following_buttons[i].text)
            shopid = following_buttons[i].get_attribute('shopid')
            following_buttons[i].click()
            time.sleep(5)
            to_add_num_of_following -= 1
            print(str(shopid) + ' is following now, ' + str(to_add_num_of_following) + ' following remains.')
        else:
            print('Skip this one. It\'s following already.')
        i += 1


# In[24]:

# 关闭
browser.quit()

