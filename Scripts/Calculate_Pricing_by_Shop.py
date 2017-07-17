# coding: utf-8
import datetime
from pandas import Series, DataFrame
import pandas as pd
import numpy as np
from Scripts.Get_Particular_Date import *
from Scripts.Get_Pricing_Report import get_concatenated_pricing_report
from Scripts.Get_Column_Name import get_column_name
from Scripts.Get_Local_Currency import get_local_currency
from Scripts.Get_Gmail_Config import *


def calculate_pricing_by_shop():
    # Pricing Report的目录
    # input_file_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
                      # 'Shopee 2016.4.12\\2016.4.23 Data Visualization\\Pricing'
    # 获取concatenated pricing report
    frame = get_concatenated_pricing_report()
    # 输出的父目录
    output_file_parent_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                              "Shopee 2016.4.12\\2017.2.21 Shop Level Summary"
    # Yesterday的公式
    yesterday = get_yesterday_date()
    # WTD公式
    start_of_this_week = get_this_monday()
    duration_of_this_week = get_wtd_duration()
    # W-1公式
    start_of_last_week = get_last_monday()
    end_of_last_week = get_last_sunday()
    # MTD公式
    start_of_this_month = get_start_of_this_month()
    end_of_this_month = get_end_of_this_month()
    duration_of_this_month = get_mtd_duration()
    # M-1公式
    start_of_last_month = get_start_of_last_month()
    end_of_last_month = get_end_of_last_month()
    duration_of_last_month = get_last_month_duration()

    # 输出csv函数
    def export_csv_to_certain_path(dataframe_name, file_name, folder_name):
        dataframe_name.to_csv(output_file_parent_path + '\\' + folder_name + '\\' + file_name + '.csv', sep=',',
                              encoding='utf-8')
        print(file_name + ' completed!')

    # 如果合并frame存在
    if frame is not False:

        # 确认日期没错
        print('Yesterday is: ' + yesterday.strftime("%Y-%m-%d") + ', Now calculating pricing result.')

        print(get_column_name(frame))
        # 转换Purchased on的格式
        frame['Purchased on'] = pd.to_datetime(frame['Purchased on'])
        frame['Purchased on (Y/m)'] = frame['Purchased on'].dt.strftime('%Y/%m')
        # left join Currency List
        currency_list = get_local_currency()
        frame = pd.merge(frame, currency_list, how='left', left_on=['Country'], right_on=['currency_name'])
        # print(frame[:1].unstack())

        # 尝试计算每月的Order
        # grouped = frame['Order ID'].groupby([frame['Purchased on (Y/m)'], frame['Country']])
        # print(grouped.count().unstack())

        # 计算GMV in USD
        frame['GMV in USD'] = (frame['Grand Total'] / frame['Currency']).apply(pd.to_numeric)

        # 尝试识别Net Order, NMV
        frame['Net Order'] = np.where(frame['Status(FE)'] == 'Cancelled', 0, 1)
        frame['NMV'] = np.where(frame['Status(FE)'] == 'Cancelled', 0, frame['GMV in USD'])
        # print(frame[:5])
        
        # 添加周数
        frame['Week Num'] = frame['Purchased on'].dt.week

        # 添加年份
        frame['Year'] = frame['Purchased on'].dt.year

        # 尝试计算每月的Gross/Net Order;外加重命名列
        # grouped1 = frame.groupby([frame['Purchased on (Y/m)']])
        # result = grouped1.agg({'Order ID': 'count', 'Net Order': 'sum', 'GMV in USD': 'sum', 'NMV': 'sum'})
        # .rename(columns={'Grand Total': 'GMV'})
        # print(result)

        # 1. 计算Yesterday Order GMV
        frame1 = frame[(frame['Purchased on'] == yesterday)]
        grouped1 = frame1.groupby([frame1['Seller User ID'], frame1['ShopId(S)'], frame1['Username(S)'],
                                   frame1['Country']])
        result1 = grouped1.agg({'Order ID': 'count', 'Net Order': 'sum', 'GMV in USD': 'sum', 'NMV': 'sum'})\
            .rename(columns={'Order ID': 'Gross Order', 'GMV in USD': 'GMV USD', 'NMV': 'NMV USD'})
        result1['ABS'] = result1['GMV USD'] / result1['Gross Order']
        export_csv_to_certain_path(result1, 'Yesterday_Order_GMV_by_Shop', 'Yesterday')

        # 2. 计算WTD Order GMV
        frame2 = frame[(frame['Purchased on'] >= start_of_this_week) & (frame['Purchased on'] <= yesterday)]
        grouped2 = frame2.groupby([frame2['Seller User ID'], frame2['ShopId(S)'], frame2['Username(S)'],
                                   frame2['Country']])
        result2 = grouped2.agg({'Order ID': 'count', 'Net Order': 'sum', 'GMV in USD': 'sum', 'NMV': 'sum'})\
            .rename(columns={'Order ID': 'Gross Order', 'GMV in USD': 'GMV USD', 'NMV': 'NMV USD'})
        result2['ABS'] = result2['GMV USD'] / result2['Gross Order']
        result2['Daily Gross Order'] = result2['Gross Order'] / duration_of_this_week
        result2['Daily GMV USD'] = result2['GMV USD'] / duration_of_this_week
        export_csv_to_certain_path(result2, 'WTD_Order_GMV_by_Shop', 'WTD')

        # 3. 计算W-1 Order GMV
        frame3 = frame[(frame['Purchased on'] >= start_of_last_week) & (frame['Purchased on'] <= end_of_last_week)]
        grouped3 = frame3.groupby([frame3['Seller User ID'], frame3['ShopId(S)'], frame3['Username(S)'],
                                   frame3['Country']])
        result3 = grouped3.agg({'Order ID': 'count', 'Net Order': 'sum', 'GMV in USD': 'sum', 'NMV': 'sum'})\
            .rename(columns={'Order ID': 'Gross Order', 'GMV in USD': 'GMV USD', 'NMV': 'NMV USD'})
        result3['ABS'] = result3['GMV USD'] / result3['Gross Order']
        result3['Daily Gross Order'] = result3['Gross Order'] / 7
        result3['Daily GMV USD'] = result3['GMV USD'] / 7
        export_csv_to_certain_path(result3, 'W_1_Order_GMV_by_Shop', 'W-1')

        # 4. 计算MTD Order GMV
        frame4 = frame[(frame['Purchased on'] >= start_of_this_month) & (frame['Purchased on'] <= yesterday)]
        grouped4 = frame4.groupby([frame4['Seller User ID'], frame4['ShopId(S)'], frame4['Username(S)'],
                                   frame4['Country']])
        result4 = grouped4.agg({'Order ID': 'count', 'Net Order': 'sum', 'GMV in USD': 'sum', 'NMV': 'sum'})\
            .rename(columns={'Order ID': 'Gross Order', 'GMV in USD': 'GMV USD', 'NMV': 'NMV USD'})
        result4['ABS'] = result4['GMV USD'] / result4['Gross Order']
        result4['Daily Gross Order'] = result4['Gross Order'] / duration_of_this_month
        result4['Daily GMV USD'] = result4['GMV USD'] / duration_of_this_month
        export_csv_to_certain_path(result4, 'MTD_Order_GMV_by_Shop', 'MTD')

        # 5. 计算M-1 Order GMV
        frame5 = frame[(frame['Purchased on'] >= start_of_last_month) & (frame['Purchased on'] <= end_of_last_month)]
        grouped5 = frame5.groupby([frame5['Seller User ID'], frame5['ShopId(S)'], frame5['Username(S)'],
                                   frame5['Country']])
        result5 = grouped5.agg({'Order ID': 'count', 'Net Order': 'sum', 'GMV in USD': 'sum', 'NMV': 'sum'})\
            .rename(columns={'Order ID': 'Gross Order', 'GMV in USD': 'GMV USD', 'NMV': 'NMV USD'})
        result5['ABS'] = result5['GMV USD'] / result5['Gross Order']
        result5['Daily Gross Order'] = result5['Gross Order'] / duration_of_last_month
        result5['Daily GMV USD'] = result5['GMV USD'] / duration_of_last_month
        export_csv_to_certain_path(result5, 'M_1_Order_GMV_by_Shop', 'M-1')

        # 6. 计算W-1/2/3/4/5 Order&Daily Order by Shops
        current_week_num = get_current_week_num()
        current_year = get_current_year()
        five_weeks_before = current_week_num - 5
        frame6 = frame[(frame['Week Num'] >= five_weeks_before) & (frame['Year'] == current_year)]
        grouped6 = frame6.groupby([frame6['Seller User ID'], frame6['ShopId(S)'], frame6['Username(S)'],
                                   frame6['Country'], frame6['Week Num']])
        result6 = grouped6.agg({'Order ID': 'count'})\
            .rename(columns={'Order ID': 'Gross Order'})
        result6 = result6.unstack('Week Num')
        result6.columns = result6.columns.droplevel(0)
        export_csv_to_certain_path(result6, 'Last_5_Weeks_Order_by_Shop', 'Cumulative')

        # 7. 计算30天Order数
        frame7 = frame[(frame['Purchased on'] >= yesterday + datetime.timedelta(days=-30))]
        grouped7 = frame7.groupby([frame7['Purchased on'], frame7['Country']])
        result7 = grouped7.agg({'Order ID': 'count'}).rename(columns={'Order ID': 'Gross Order'})
        result7 = result7.unstack('Country')
        result7.columns = result7.columns.droplevel(0)
        export_csv_to_certain_path(result7, 'D-30 Order by Country', 'Cumulative')

        # 所有步骤执行完后
        print('\nProcess completed!')
        send_message('enzo.kuang@shopeemobile.com', '[Notices] ' + str(get_today_date()) +
                     ' Order Calculation Completed!', 'Order Calculation Completed!')

if __name__ == '__main__':
    calculate_pricing_by_shop()
