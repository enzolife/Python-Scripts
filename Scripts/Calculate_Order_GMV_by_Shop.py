# coding: utf-8
import datetime
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from Scripts.Get_Particular_Date import *
from Scripts.Get_Order_Report import get_concatenated_order_report
from Scripts.Get_Column_Name import get_column_name
from Scripts.Get_Local_Currency import get_local_currency

# Order Report的目录
input_file_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
                  'Shopee 2016.4.12\\2016.4.23 Data Visualization\\Order'
# 获取concatenated order report
frame = get_concatenated_order_report(input_file_path)
# 输出的父目录
output_file_parent_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                          "Shopee 2016.4.12\\2017.2.21 Shop Level Summary"
# Yesterday的公式
yesterday = get_yesterday_date()
# WTD公式
start_of_this_week = get_this_monday()
# W-1公式
start_of_last_week = get_last_monday()
end_of_last_week = get_last_sunday()
# MTD公式
start_of_this_month = get_start_of_this_month()
end_of_this_month = get_end_of_this_month()
# M-1公式
start_of_last_month = get_start_of_last_month()
end_of_last_month = get_end_of_last_month()
# 如果合并frame存在
if frame is not False:
    print(get_column_name(frame))
    # 转换Purchased on的格式
    frame['Purchased on'] = pd.to_datetime(frame['Purchased on'])
    frame['Purchased on (Y/m)'] = frame['Purchased on'].dt.strftime('%Y/%m')
    # left join Currency List
    # currency_list = get_local_currency()
    # frame = pd.merge(frame, currency_list, how='left', left_on=['Country'], right_on=['currency_name'])
    # print(frame[:1].unstack())

    # 尝试计算每月的Order
    # grouped = frame['Order ID'].groupby([frame['Purchased on (Y/m)'], frame['Country']])
    # print(grouped.count().unstack())

    # 尝试识别Net Order
    frame['Net Order'] = np.where(frame['Status(FE)'] == 'Cancelled', 0, 1)
    frame['NMV'] = np.where(frame['Status(FE)'] == 'Cancelled', 0, frame['Grand Total'])
    # print(frame[:5])
    # 尝试计算每月的Gross/Net Order;外加重命名列
    grouped1 = frame.groupby([frame['Purchased on (Y/m)']])
    result = grouped1.agg({'Order ID': 'count', 'Net Order': 'sum', 'Grand Total': 'sum', 'NMV': 'sum'})\
        .rename(columns={'Grand Total': 'GMV'})
    print(result)
    # 1. 计算Yesterday
    # 所有步骤执行完后
    print('\nProcess completed!')
else:
    print('\nData not downloaded yet!')
