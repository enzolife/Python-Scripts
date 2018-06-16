
# coding: utf-8

# In[30]:

from PIL import Image
import tesserocr

from selenium import webdriver
from PIL import Image


# In[31]:

# 屏幕最大化，且指定下载目录
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")

prefs = {"profile.default_content_settings.popups": 0,
         "download.default_directory": r"D:\Program Files (x86)\百度云同步盘\Dropbox\-E·J- 2014.5.1\2016.12.15 店小秘数据分析\\", # IMPORTANT - ENDING SLASH V IMPORTANT
         "directory_upgrade": True}
options.add_experimental_option("prefs", prefs)


# In[32]:

# 使用chromedriver才可以用开发者权限
chrome_driver_path = "D://Program Files (x86)//百度云同步盘//我的软件//chromedriver.exe"
browser = webdriver.Chrome(chrome_driver_path, chrome_options=options)


# In[33]:

browser.get('https://www.dianxiaomi.com/')


# In[34]:

acc_password_input_elem = browser.find_element_by_id('loginImgVcode')


# In[35]:

location = acc_password_input_elem.location;
size = acc_password_input_elem.size;


# In[37]:

browser.save_screenshot("image.png");

x = location['x'];
y = location['y'];
width = location['x']+size['width'];
height = location['y']+size['height'];

im = Image.open('image.png')
im = im.crop((int(x), int(y), int(width), int(height)))
im.save('image_edited.png')


# In[40]:

p7 = Image.open('image_edited.png')
tesserocr.image_to_text(p7)


# In[ ]:



