
# coding: utf-8

# In[1]:



from pandas import Series, DataFrame
import pandas as pd
import glob
import os
from Get_File_Create_Time import creation_date
from Get_Particular_Date import *


# In[41]:

def to_check_whether_all_listings_today_are_downloaded(path):
    
    country_list = []
    
    allFiles = glob.glob(path + "\\*\\*.csv")
    
    frame = pd.DataFrame()
    list_ = []
    for file_ in allFiles:
        pwd = os.getcwd() # 首先取初始工作目录
        os.chdir(os.path.dirname(file_)) # 然后取SG/MY/TW/ID/TH这个文件夹
        
        country_name = os.path.basename(file_).split('_')[0]
        file_create_time = creation_date(file_)
        today_date = get_today_date()

        # 如果creation_date不是今天，就跳出
        if file_create_time != today_date:
            print('Data Downloaded Today!')
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
        
    return "finish"

