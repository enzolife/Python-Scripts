# coding: utf-8
import pandas as pd
import os
from get_particular_date import *
from get_listing_reports import get_concatenated_listing_report
from get_gmail_config import send_message
from get_google_sheets import *
from calculate_bd_index import *
from get_seller_index import get_seller_index_from_google_sheet


def calculate_sku_by_shop():
    # Listing Report的目录
    # input_file_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
    # 'Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing'
    frame = get_concatenated_listing_report()
    print('listing reports are concatenating.\n')

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
    # M-1公式
    start_of_last_month = get_start_of_last_month()
    end_of_last_month = get_end_of_last_month()

    # 如果合并frame存在
    if frame is not False:

        # 确认日期没错
        print('Yesterday is: ' + yesterday.strftime("%Y-%m-%d") + ', Now calculating sku by shop result.')
        # 转换Date Created的格式
        frame['Date Created'] = pd.to_datetime(frame['Date Created'])
        # Merge Seller Index
        seller_index = get_seller_index_from_google_sheet()

        # 1. 计算New SKUs / New Live SKUs by KAMs
        # 1.1 计算New SKUs / New Live SKUs by KAMs的函数
        def calculate_num_of_sku(date_period_name, start_date, end_date, file_name, live):

            # 如果计算Live，则添加Live的判断
            if live is True:
                pre_frame = frame[(frame['Date Created'] >= start_date) & (frame['Date Created'] <= end_date)
                                  & (frame['Live_status'] == 'live SKUs')]
                column_name = date_period_name + ' Live SKUs'
            else:
                pre_frame = frame[(frame['Date Created'] >= start_date) & (frame['Date Created'] <= end_date)]
                column_name = date_period_name + ' SKUs'

            # 分组计算
            group = pre_frame['Product ID'].groupby([pre_frame['Shop ID'], pre_frame['Country']])
            output_frame = group.agg({'Product ID': 'count'}) \
                .rename(columns={'Product ID': column_name})
            output_frame = pd.DataFrame(output_frame).reset_index()
            output_frame = output_frame.sort(['Country', column_name]
                                             , ascending=[True, False])
            return output_frame

        # 1.2 两个Data Frame合并
        def merge_sku_df(new_skus_frame, new_live_skus_frame):
            merged_frame = pd.merge(new_skus_frame, new_live_skus_frame, how='left'
                                    , on=['Shop ID', 'Country'])
            return merged_frame

        # 1.3 需要输出的列表
        output_file_list = [['Yesterday', yesterday, yesterday, 'Yesterday New SKUs by KAM'],
                            ['MTD', start_of_this_month, yesterday, 'MTD New SKUs by KAM'],
                            ['M-1', start_of_last_month, end_of_last_month, 'M-1 New SKUs by KAM'],
                            ['WTD', start_of_this_week, yesterday, 'WTD New SKUs by KAM'],
                            ['W-1', start_of_last_week, end_of_last_week, 'W-1 New SKUs by KAM'],
                            ['Cumulative', datetime.date(1900, 1, 1), yesterday, 'Cumulative SKUs by KAM']]

        # 1.4 历遍输出
        for date_period_name, start_date, end_date, file_name in output_file_list:
            new_skus_frame = calculate_num_of_sku(date_period_name, start_date, end_date, file_name, False)
            new_live_skus_frame = calculate_num_of_sku(date_period_name, start_date, end_date, file_name, True)
            merged_df = merge_sku_df(new_skus_frame, new_live_skus_frame)
            # 与Seller Index合并并计算
            merged_df = pd.merge(merged_df, seller_index, how='left', left_on=['Shop ID'], right_on=['Child ShopID'])
            group = merged_df.groupby([merged_df['GP Account Owner'], merged_df['Country']])
            output_frame = group.agg({date_period_name + ' SKUs': 'sum',
                                      date_period_name + ' Live SKUs': 'sum'})
            merged_df = pd.DataFrame(output_frame).reset_index()

            # 输出到本地
            output_file_folder_path = os.path.join(output_file_parent_path, date_period_name)
            output_file_path = os.path.join(output_file_folder_path, file_name + '.csv')
            merged_df.to_csv(output_file_path, sep=',', index=False)
            print('%s is completed' % file_name)
            # 上传到GP Account Owner Performance Report (Daily)
            upload_dataframe_to_google_sheet(merged_df
                                             , '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
                                             , file_name)




        # 更新相关表的last update time
        # 更新GP Account Owner Performance Report (Daily)
        upload_last_update_time('1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM', 'Description', 'D5')
        # 更新BD Performance Report (Daily)
        # upload_last_update_time('1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8', 'Description', 'D6')

        # 所有步骤执行完后，发一封邮件
        print('\nProcess completed!')
        send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date())
                     + ' SKU by Shop Calculation Completed!', 'SKU Calculation Completed!')


if __name__ == '__main__':
    calculate_sku_by_shop()
