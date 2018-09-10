# coding: utf-8
import os
import pandas as pd
from get_particular_date import *
from get_listing_reports import get_concatenated_listing_report
from get_gmail_config import send_message
from get_seller_index import get_certain_google_sheets_to_dataframe
from get_google_sheets import upload_dataframe_to_google_sheet
from get_seller_index import get_seller_index_from_google_sheet


def calculate_sku_by_cat_product():
    # Listing Report的目录
    # input_file_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
    # 'Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing'
    frame = get_concatenated_listing_report()
    print('listing reports are concatenating.\n')

    # 输出的父目录
    output_file_parent_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                              "Shopee 2016.4.12\\2017.4.14 Product Level Summary"

    # 如果合并frame存在
    if frame is not False:
        # 确认日期没错
        print('Yesterday is: ' + get_yesterday_date().strftime("%Y-%m-%d")
              + ', Now calculating sku by cat / product result.')
        # Merge Seller Index
        seller_index = get_seller_index_from_google_sheet()
        frame = pd.merge(frame, seller_index, how='left', left_on=['Shop ID'], right_on=['Child ShopID'])
        # 转换Date Created的格式
        frame['Date Created'] = pd.to_datetime(frame['Date Created'])

        # 1 计算New SKUs / New Live SKUs by Cat/Sub Cat的函数
        def calculate_num_of_sku(date_period_name, start_date, end_date, file_name, live):
            # 如果计算Live，则添加Live的判断
            if live is True:
                pre_frame = frame[(frame['Date Created'] >= start_date) & (frame['Date Created'] <= end_date)
                                  & (frame['Live_status'] == 'live SKUs')]
                column_name = ' Live SKUs'
            else:
                pre_frame = frame[(frame['Date Created'] >= start_date) & (frame['Date Created'] <= end_date)]
                column_name = ' SKUs'
            # 分组计算
            group = pre_frame['Product ID'].groupby([pre_frame['Country'], pre_frame['Category']
                                                        , pre_frame['Sub category']])
            output_frame = group.agg({'Product ID': 'count'}) \
                .rename(columns={'Product ID': date_period_name + column_name})
            output_frame = pd.DataFrame(output_frame).reset_index()
            return output_frame

        # 1 两个Data Frame合并
        def merge_sku_df(new_skus_frame, new_live_skus_frame):
            merged_frame = pd.merge(new_skus_frame, new_live_skus_frame, how='left'
                                    , on=['Country', 'Category', 'Sub category'])
            return merged_frame

        # 2 计算New SKUs / New Live SKUs by KAM by Cat的函数
        def calculate_num_of_sku_by_kam(date_period_name, start_date, end_date, file_name, live):
            # 如果计算Live，则添加Live的判断
            if live is True:
                pre_frame = frame[(frame['Date Created'] >= start_date) & (frame['Date Created'] <= end_date)
                                  & (frame['Live_status'] == 'live SKUs')]
                column_name = 'New Live SKUs'
            else:
                pre_frame = frame[(frame['Date Created'] >= start_date) & (frame['Date Created'] <= end_date)]
                column_name = 'New SKUs'
            # 分组计算
            group = pre_frame['Product ID'].groupby([pre_frame['GP Account Owner'], pre_frame['Country'], pre_frame['Category']
                                                        , pre_frame['Sub category']])
            output_frame = group.agg({'Product ID': 'count'}) \
                .rename(columns={'Product ID': column_name})
            output_frame = pd.DataFrame(output_frame).reset_index()
            return output_frame

        # 2 两个Data Frame合并
        def merge_sku_by_kam_df(new_skus_frame, new_live_skus_frame):
            merged_frame = pd.merge(new_skus_frame, new_live_skus_frame, how='left'
                                    , on=['GP Account Owner', 'Country', 'Category', 'Sub category'])
            return merged_frame

        # 1.1 New SKUs / New Live SKUs by Cat/Sub Cat需要输出的列表
        output_file_list = [['Yesterday', get_yesterday_date(), get_yesterday_date(), 'Yesterday New SKUs by Cat'],
                            ['MTD', get_start_of_this_month(), get_yesterday_date(), 'MTD New SKUs by Cat'],
                            ['M-1', get_start_of_last_month(), get_end_of_last_month(), 'M-1 New SKUs by Cat'],
                            ['WTD', get_this_monday(), get_yesterday_date(), 'WTD New SKUs by Cat'],
                            ['W-1', get_last_monday(), get_last_sunday(), 'W-1 New SKUs by Cat'],
                            ['Cumulative', datetime.date(1900, 1, 1), get_yesterday_date(), 'Cumulative SKUs by Cat']]

        # 1.2 New SKUs / New Live SKUs by Cat/Sub Cat历遍输出
        for date_period_name, start_date, end_date, file_name in output_file_list:
            new_skus_frame = calculate_num_of_sku(date_period_name, start_date, end_date, file_name, False)
            new_live_skus_frame = calculate_num_of_sku(date_period_name, start_date, end_date, file_name, True)
            merged_df = merge_sku_df(new_skus_frame, new_live_skus_frame)
            output_file_folder_path = os.path.join(output_file_parent_path, date_period_name)
            # 输出
            output_file_path = os.path.join(output_file_folder_path, file_name + '.csv')
            merged_df.to_csv(output_file_path, sep=',', index=False)
            # 上传到Category Performance Report (CB)
            upload_dataframe_to_google_sheet(merged_df
                                             , '1DuEL14i9DveAol0JyMJco4ErPw4LsDNOI4ptoxYUheM'
                                             , file_name)

            print('%s is completed' % file_name)

        # 2.1 by cat by KAM需要输出的列表
        output_file_list = [['Yesterday', get_yesterday_date(), get_yesterday_date(), 'Yesterday New SKUs by Cat by KAM'],
                            ['MTD', get_start_of_this_month(), get_yesterday_date(), 'MTD New SKUs by Cat by KAM'],
                            ['M-1', get_start_of_last_month(), get_end_of_last_month(), 'M-1 New SKUs by Cat by KAM'],
                            ['WTD', get_this_monday(), get_yesterday_date(), 'WTD New SKUs by Cat by KAM'],
                            ['W-1', get_last_monday(), get_last_sunday(), 'W-1 New SKUs by Cat by KAM'],
                            ['Cumulative', datetime.date(1900, 1, 1), get_yesterday_date(), 'Cumulative SKUs by Cat by KAM']]

        # 2.2 by cat by KAM历遍输出
        for date_period_name, start_date, end_date, file_name in output_file_list:
            new_skus_frame = calculate_num_of_sku_by_kam(date_period_name, start_date, end_date, file_name, False)
            new_live_skus_frame = calculate_num_of_sku_by_kam(date_period_name, start_date, end_date, file_name, True)
            merged_df = merge_sku_by_kam_df(new_skus_frame, new_live_skus_frame)
            output_file_folder_path = os.path.join(output_file_parent_path, date_period_name)
            # 输出
            output_file_path = os.path.join(output_file_folder_path, file_name + '.csv')
            merged_df.to_csv(output_file_path, sep=',', index=False)
            # 上传至Category Performance Report (CB)，只上传MTD
            # 首先去掉New Live SKUs列，然后转置
            if date_period_name == 'MTD':
                merged_df = merged_df[['GP Account Owner', 'Country', 'Category', 'Sub category', 'New SKUs']]
                # 重新设置index
                merged_df = merged_df.set_index(['Country', 'Category', 'Sub category', 'GP Account Owner'])
                merged_df = merged_df.unstack('GP Account Owner').reset_index()
                # 丢掉第一行
                merged_df.columns = merged_df.columns.droplevel(0)
                # 补充标题
                merged_df.columns.values[0] = 'Country'
                merged_df.columns.values[1] = 'Category'
                merged_df.columns.values[2] = 'Sub Category'
                upload_dataframe_to_google_sheet(merged_df
                                                 , '1DuEL14i9DveAol0JyMJco4ErPw4LsDNOI4ptoxYUheM'
                                                 , file_name)

            print('%s is completed' % file_name)

        # 所有步骤执行完后，发一封邮件
        print('\nProcess completed!')
        send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date())
                     + ' SKU by Cat / Product Calculation Completed!', 'SKU by Cat / Product Calculation Completed!')


if __name__ == '__main__':
    calculate_sku_by_cat_product()
