# coding: utf-8
import datetime
from pandas import Series, DataFrame
import pandas as pd
from Get_Particular_Date import *
from Get_Listing_Reports import get_concatenated_listing_report

input_file_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing'
frame = get_concatenated_listing_report(input_file_path)

# 输出的目录
output_file_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2017.2.21 Shop Level Summary\\Yesterday\\"

# 求昨天的公式
d = get_yesterday_date()

# 如果合并frame存在
if frame is not False:

    # 转换Date Created的格式
    frame['Date Created'] = pd.to_datetime(frame['Date Created'])

    # 计算Yesterday New SKUs
    frame1 = frame[(frame['Date Created'] == d)]
    grouped1 = frame1['Product ID'].groupby([frame1['Seller User ID'], frame1['Shop ID'], frame1['Username'], frame1['Country']])

    Yesterday_New_SKUs_by_Shop = grouped1.agg({'Product ID': {'New SKUs': 'count'}})
    Yesterday_New_SKUs_by_Shop.columns = Yesterday_New_SKUs_by_Shop.columns.droplevel(0)

    Yesterday_New_SKUs_by_Shop.to_csv(output_file_path + 'Yesterday_New_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

    print('Yesterday_New_SKUs_by_Shop completed')

    # 计算Yesterday New Live SKUs
    frame2 = frame[(frame['Date Created'] == d) & (frame['Status'] == 'Normal')]
    grouped2 = frame2['Product ID'].groupby([frame2['Seller User ID'], frame2['Shop ID'], frame2['Username'], frame2['Country']])

    Yesterday_New_Live_SKUs_by_Shop = grouped2.agg({'Product ID': {'New Live SKUs': 'count'}})
    Yesterday_New_Live_SKUs_by_Shop.columns = Yesterday_New_Live_SKUs_by_Shop.columns.droplevel(0)

    Yesterday_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'Yesterday_New_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

    print('Yesterday_New_Live_SKUs_by_Shop completed')

    # 计算Cumulative SKUs
    grouped3 = frame['Product ID'].groupby([frame['Seller User ID'], frame['Shop ID'], frame['Username'], frame['Country']])

    Cumulative_SKUs_by_Shop = grouped3.agg({'Product ID': {'Cumulative SKUs': 'count'}})
    Cumulative_SKUs_by_Shop.columns = Cumulative_SKUs_by_Shop.columns.droplevel(0)

    Cumulative_SKUs_by_Shop.to_csv(output_file_path + 'Cumulative_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

    print('Cumulative_SKUs_by_Shop completed')

    # 计算Cumulative Live SKUs
    frame4 = frame.loc[frame['Status'] == 'Normal']
    grouped4 = frame4['Product ID'].groupby([frame4['Seller User ID'], frame4['Shop ID'], frame4['Username'], frame4['Country']])

    Cumulative_Live_SKUs_by_Shop = grouped4.agg({'Product ID': {'Cumulative Live SKUs': 'count'}})
    Cumulative_Live_SKUs_by_Shop.columns = Cumulative_Live_SKUs_by_Shop.columns.droplevel(0)

    Cumulative_Live_SKUs_by_Shop.to_csv(output_file_path + 'Cumulative_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

    print('Cumulative_Live_SKUs_by_Shop completed')

    print('Process completed!')

else:
    print('Data not downloaded yet!')
