# coding: utf-8
import datetime
from pandas import Series, DataFrame
import pandas as pd

from Get_Listing_Reports import get_concatenated_listing_report

path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing' # use your path
frame = get_concatenated_listing_report(path)

# 求昨天的公式
d = datetime.date.today() + datetime.timedelta(days=-1)

# 输出的目录
output_file_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2017.2.21 Shop Level Summary\\Yesterday\\"

# 计算Yesterday New SKUs
frame['Date Created'] = pd.to_datetime(frame['Date Created'])

frame3 = frame[(frame['Date Created']==d)]
grouped3 = frame3['Product ID'].groupby([frame3['Seller User ID'],frame3['Shop ID'],frame3['Username'],frame3['Country']])

Yesterday_New_SKUs_by_Shop = grouped3.agg({'Product ID':{'New SKUs': 'count'}})
Yesterday_New_SKUs_by_Shop.columns = Yesterday_New_SKUs_by_Shop.columns.droplevel(0)

Yesterday_New_SKUs_by_Shop.to_csv(output_file_path + 'Yesterday_New_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

# 计算Yesterday New Live SKUs
frame4 = frame[(frame['Date Created']==d) & (frame['Status'] == 'Normal')]
grouped4 = frame4['Product ID'].groupby([frame4['Seller User ID'],frame4['Shop ID'],frame4['Username'],frame4['Country']])

Yesterday_New_Live_SKUs_by_Shop = grouped4.agg({'Product ID':{'New Live SKUs': 'count'}})
Yesterday_New_Live_SKUs_by_Shop.columns = Yesterday_New_Live_SKUs_by_Shop.columns.droplevel(0)

Yesterday_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'Yesterday_New_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

# 计算Cumulative SKUs
grouped = frame['Product ID'].groupby([frame['Seller User ID'],frame['Shop ID'],frame['Username'],frame['Country']])

Cumulative_SKUs_by_Shop = grouped.agg({'Product ID':{'Cumulative SKUs': 'count'}})
Cumulative_SKUs_by_Shop.columns = Cumulative_SKUs_by_Shop.columns.droplevel(0)

Cumulative_SKUs_by_Shop.to_csv(output_file_path + 'Cumulative_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

# 计算Cumulative Live SKUs
frame2 = frame.loc[frame['Status'] == 'Normal']
grouped2 = frame2['Product ID'].groupby([frame2['Seller User ID'],frame2['Shop ID'],frame2['Username'],frame2['Country']])

Cumulative_Live_SKUs_by_Shop = grouped2.agg({'Product ID':{'Cumulative Live SKUs': 'count'}})
Cumulative_Live_SKUs_by_Shop.columns = Cumulative_Live_SKUs_by_Shop.columns.droplevel(0)

Cumulative_Live_SKUs_by_Shop.to_csv(output_file_path + 'Cumulative_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')
