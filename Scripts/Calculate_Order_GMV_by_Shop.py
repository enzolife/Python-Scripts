# coding: utf-8
import datetime
from pandas import Series, DataFrame
import pandas as pd
from Get_Particular_Date import *
from Get_Order_Report import get_concatenated_order_report
from Get_Column_Name import get_column_name

input_file_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2016.4.23 Data Visualization\\Order'
frame = get_concatenated_order_report(input_file_path)

# 输出的父目录
output_file_parent_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2017.2.21 Shop Level Summary"

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

    # print(get_column_name(frame))

    # 转换Purchased on的格式
    frame['Purchased on'] = pd.to_datetime(frame['Purchased on'])

    # 1. 计算Yesterday

    # 所有步骤执行完后
    print('\nProcess completed!')

else:
    print('\nData not downloaded yet!')
