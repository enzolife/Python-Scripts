# coding: utf-8
import os
import pandas as pd
from Scripts.Get_Particular_Date import *
from Scripts.Get_Pricing_Report import get_concatenated_pricing_report
from Scripts.Get_Local_Currency import get_local_currency
from Scripts.Get_Gmail_Config import send_message
from Scripts.Get_Google_Sheets import upload_dataframe_to_google_sheet


def calculate_pricing_by_cat_product():
    # 获取concatenated pricing report
    frame = get_concatenated_pricing_report()
    print('pricing reports are concatenating.\n')
    # 输出的父目录
    output_file_parent_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                              "Shopee 2016.4.12\\2017.4.14 Product Level Summary"

    # 如果合并frame存在
    if frame is not False:
        # 确认日期没错
        print('Yesterday is: ' + get_yesterday_date().strftime("%Y-%m-%d") + ', Now calculating pricing result.')
        # 因为Model ID的问题，产生了很多重复行，现在进行去重
        frame = frame.drop_duplicates(subset=['Order ID', 'Product ID'])
        # 转换Purchased Time的格式
        frame['Purchased Time'] = pd.to_datetime(frame['Purchased Time'])
        frame['Purchased Time (Y/m)'] = frame['Purchased Time'].dt.strftime('%Y/%m')
        # 转换Specific Purchase Time的格式
        frame['Specific purchase time'] = pd.to_datetime(frame['Specific purchase time'],
                                                         format='%d/%m/%Y, %H:%M:%S %p')
        # left join Currency List
        currency_list = get_local_currency()
        frame = pd.merge(frame, currency_list, how='left', left_on=['Country'], right_on=['currency_name'])
        # 添加周数
        frame['Week Num'] = frame['Purchased Time'].dt.week
        # 添加年份
        frame['Year'] = frame['Purchased Time'].dt.year
        # 添加年/月
        frame['Year/Month'] = frame['Purchased Time'].dt.strftime('%Y-%m')
        # 添加小时
        frame['Hour'] = frame['Specific purchase time'].dt.hour

        # 求Normalized Order
        normalized_order_group = frame['Product ID'].groupby([frame['Order ID']])
        normalized_order_frame = normalized_order_group.agg({'Product ID': 'count'})
        normalized_order_frame['Normalized Order'] = 1 / normalized_order_frame['Product ID']
        normalized_order_frame = pd.DataFrame(normalized_order_frame).reset_index()

        # Merge到原来的frame
        frame = pd.merge(frame, normalized_order_frame, how='left', left_on=['Order ID'], right_on=['Order ID'])

        # 开始计算
        # 1 计算Order by Cat
        # 1.1 Order by cat需要输出的列表
        output_file_list = [['Yesterday', get_yesterday_date(), get_yesterday_date(),
                             1, 'Yesterday Gross Order by Cat'],
                            ['MTD', get_start_of_this_month(), get_yesterday_date(),
                             get_mtd_duration(), 'MTD Gross Order by Cat'],
                            ['M-1', get_start_of_last_month(), get_end_of_last_month(),
                             get_last_month_duration(), 'M-1 Gross Order by Cat'],
                            ['WTD', get_this_monday(), get_yesterday_date(),
                             get_wtd_duration(), 'WTD Gross Order by Cat'],
                            ['W-1', get_last_monday(), get_last_sunday(),
                             7, 'W-1 Gross Order by Cat']]

        # 1.2 计算Order by cat的函数
        def calculate_order_by_cat(date_period_name, start_date, end_date, duration, file_name):
            pre_frame = frame[(frame['Purchased Time'] >= start_date) & (frame['Purchased Time'] <= end_date)]
            group = pre_frame['Normalized Order'].groupby([pre_frame['Country'], pre_frame['Category']
                                                              , pre_frame['Sub category']])
            output_frame = group.agg({'Normalized Order': 'sum'}) \
                .rename(columns={'Normalized Order': 'Gross_Order'})
            output_frame['Avg_Daily_Order'] = output_frame['Gross_Order'] / duration
            output_frame = pd.DataFrame(output_frame).reset_index()
            output_frame = output_frame.sort_values(['Country', 'Category', 'Avg_Daily_Order']
                                                    , ascending=[True, True, False])
            return output_frame

        # 1.3 开始历遍
        for date_period_name, start_date, end_date, duration, file_name in output_file_list:
            order_by_cat_frame = calculate_order_by_cat(date_period_name, start_date, end_date, duration, file_name)
            output_file_folder_path = os.path.join(output_file_parent_path, date_period_name)
            # 输出
            output_file_path = os.path.join(output_file_folder_path, file_name + '.csv')
            order_by_cat_frame.to_csv(output_file_path, sep=',', index=False)
            # 上传
            upload_dataframe_to_google_sheet(order_by_cat_frame,
                                             '1DuEL14i9DveAol0JyMJco4ErPw4LsDNOI4ptoxYUheM',
                                             file_name)
            print('%s is completed' % file_name)

        # 2 计算Order by Cat by KAM

        # 3 计算Order by Cat by Hour
        # 3.1 Order by cat by hour需要输出的列表
        output_file_list = [['Yesterday', get_yesterday_date(), get_yesterday_date(),
                             1, 'Yesterday Gross Order by Cat by Hour'],
                            ['MTD', get_start_of_this_month(), get_yesterday_date(),
                             get_mtd_duration(), 'MTD Gross Order by Cat by Hour'],
                            ['M-1', get_start_of_last_month(), get_end_of_last_month(),
                             get_last_month_duration(), 'M-1 Gross Order by Cat by Hour'],
                            ['WTD', get_this_monday(), get_yesterday_date(),
                             get_wtd_duration(), 'WTD Gross Order by Cat by Hour'],
                            ['W-1', get_last_monday(), get_last_sunday(),
                             7, 'W-1 Gross Order by Cat by Hour']]

        # 3.2 计算Order by cat by hour的函数
        def calculate_order_by_cat_by_hour(date_period_name, start_date, end_date, duration, file_name):
            pre_frame = frame[(frame['Purchased Time'] >= start_date) & (frame['Purchased Time'] <= end_date)]
            group = pre_frame['Normalized Order'].groupby([pre_frame['Country'], pre_frame['Category']
                                                              , pre_frame['Hour']])
            output_frame = group.agg({'Normalized Order': 'sum'}) \
                .rename(columns={'Normalized Order': 'Gross_Order'})
            output_frame = output_frame.unstack('Hour')
            output_frame = pd.DataFrame(output_frame).reset_index()
            output_frame.columns = output_frame.columns.droplevel(0)
            return output_frame

        # 3.3 开始历遍
        for date_period_name, start_date, end_date, duration, file_name in output_file_list:
            order_by_cat_frame = calculate_order_by_cat_by_hour(date_period_name, start_date, end_date, duration, file_name)
            output_file_folder_path = os.path.join(output_file_parent_path, date_period_name)
            # 输出
            output_file_path = os.path.join(output_file_folder_path, file_name + '.csv')
            order_by_cat_frame.to_csv(output_file_path, sep=',', index=False)
            print('%s is completed' % file_name)

        # 4 计算Order by Cat by Month
        output_by_cat_by_month_group = frame['Normalized Order'].groupby([frame['Country']
                                                                             , frame['Category']
                                                                             , frame['Sub category']
                                                                             , frame['Year/Month']])
        output_by_cat_by_month_frame = output_by_cat_by_month_group.agg({'Normalized Order': 'sum'})\
            .rename(columns={'Normalized Order': 'Gross_Order'})
        output_by_cat_by_month_frame = output_by_cat_by_month_frame.unstack('Year/Month')
        output_by_cat_by_month_frame = pd.DataFrame(output_by_cat_by_month_frame).reset_index()
        output_by_cat_by_month_frame.columns = output_by_cat_by_month_frame.columns.droplevel(0)
        # 补充两列列名，不然上传会报错
        output_by_cat_by_month_frame.columns.values[0] = 'Country'
        output_by_cat_by_month_frame.columns.values[1] = 'Category'
        output_by_cat_by_month_frame.columns.values[2] = 'Sub Category'
        # 上传
        upload_dataframe_to_google_sheet(output_by_cat_by_month_frame,
                                         '1ETYWXovdUPI_yPhtw0mo1VwoYmCFztHu3dNQu0O5FEw',
                                         'Gross Order by Cat by Month')

        # 所有步骤执行完后
        print('\nProcess completed!')
        send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date())
                     + ' Pricing by Cat Product Calculation Completed!'
                     , 'Pricing by Cat Product Calculation Completed!')


if __name__ == '__main__':
    calculate_pricing_by_cat_product()
