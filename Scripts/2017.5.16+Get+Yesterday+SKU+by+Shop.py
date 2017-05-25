
# coding: utf-8

# In[1]:

from pandas import Series, DataFrame
import pandas as pd
import glob


# In[2]:

path ='D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing' # use your path
allFiles = glob.glob(path + "\\*\\*.csv")
frame = pd.DataFrame()
list_ = []
for file_ in allFiles:
    df = pd.read_csv(file_,index_col=None, header=0)
    list_.append(df)
frame = pd.concat(list_)


# In[3]:

# 求昨天的公式
import datetime
d = datetime.date.today() + datetime.timedelta(days=-1)


# In[4]:

# 输出的目录
output_file_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2017.2.21 Shop Level Summary\\Yesterday\\"


# In[5]:

# 计算Yesterday New SKUs
frame['Date Created']= pd.to_datetime(frame['Date Created'])

frame3 = frame[(frame['Date Created']==d)]
grouped3 = frame3['﻿Product ID'].groupby([frame3['Seller User ID'],frame3['Shop ID'],frame3['Username'],frame3['Country']])

Yesterday_New_SKUs_by_Shop = grouped3.agg({'Product ID':{'New SKUs': 'count'}})
Yesterday_New_SKUs_by_Shop.columns = Yesterday_New_SKUs_by_Shop.columns.droplevel(0)


# In[6]:

Yesterday_New_SKUs_by_Shop.to_csv(output_file_path + 'Yesterday_New_SKUs_by_Shop.csv', sep=',', encoding='utf-8')


# In[7]:

# 计算Yesterday New Live SKUs
frame4 = frame[(frame['Date Created']==d) & (frame['Status'] == 'Normal')]
grouped4 = frame4['﻿Product ID'].groupby([frame4['Seller User ID'],frame4['Shop ID'],frame4['Username'],frame4['Country']])

Yesterday_New_Live_SKUs_by_Shop = grouped4.agg({'Product ID':{'New Live SKUs': 'count'}})
Yesterday_New_Live_SKUs_by_Shop.columns = Yesterday_New_Live_SKUs_by_Shop.columns.droplevel(0)


# In[8]:

Yesterday_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'Yesterday_New_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')


# In[9]:

# 计算Cumulative SKUs
grouped = frame['﻿Product ID'].groupby([frame['Seller User ID'],frame['Shop ID'],frame['Username'],frame['Country']])

Cumulative_SKUs_by_Shop = grouped.agg({'Product ID':{'Cumulative SKUs': 'count'}})
Cumulative_SKUs_by_Shop.columns = Cumulative_SKUs_by_Shop.columns.droplevel(0)


# In[10]:

Cumulative_SKUs_by_Shop.to_csv(output_file_path + 'Cumulative_SKUs_by_Shop.csv', sep=',', encoding='utf-8')


# In[11]:

# 计算Cumulative Live SKUs
frame2 = frame.loc[frame['Status'] == 'Normal']
grouped2 = frame2['﻿Product ID'].groupby([frame2['Seller User ID'],frame2['Shop ID'],frame2['Username'],frame2['Country']])

Cumulative_Live_SKUs_by_Shop = grouped2.agg({'Product ID':{'Cumulative Live SKUs': 'count'}})
Cumulative_Live_SKUs_by_Shop.columns = Cumulative_Live_SKUs_by_Shop.columns.droplevel(0)


# In[12]:

Cumulative_Live_SKUs_by_Shop.to_csv(output_file_path + 'Cumulative_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

