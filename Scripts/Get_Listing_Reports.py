
# coding: utf-8

# In[1]:



from pandas import Series, DataFrame
import pandas as pd
import glob
import os
import datetime
import time
from Get_File_Create_Modify_Time import last_modify_date
from Get_Particular_Date import *


# In[41]:

def get_concatenated_listing_report(path):
    
    country_list = []
    
    allFiles = glob.glob(path + "\\*\\*.csv")

    frame = pd.DataFrame()
    list_ = []
    for file_ in allFiles:
        pwd = os.getcwd() # 首先取初始工作目录
        os.chdir(os.path.dirname(file_)) # 然后取SG/MY/TW/ID/TH这个文件夹
        
        country_name = os.path.basename(file_).split('_')[0]
        file_create_time = last_modify_date(file_)
        today_date = get_today_date().strftime("%Y-%m-%d")

        # 如果creation_date不是今天，就跳出
        if file_create_time != today_date:
            break
        else:
            # 如果原来已经有了这个国家，就不用添加进去了
            if country_name not in country_list:

                country_list.append(country_name)

            country_list.sort()
    
    # 如果所有国家都齐备
    if country_list == ['ID','MY','SG','TH','TW']:
        for file_ in allFiles:
            pwd = os.getcwd() # 首先取初始工作目录
            os.chdir(os.path.dirname(file_)) # 然后取SG/MY/TW/ID/TH这个文件夹

            df = pd.read_csv(os.path.basename(file_),index_col=None, header=0) # 读取这份文件，不用带上前面那一堆路径
            list_.append(df)

            os.chdir(pwd)

        frame = pd.concat(list_)
        
        return frame
    else:
        return False

# use your path
# path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing"
# get_concatenated_listing_report(path))

