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

        # 1.3 合并后Left Join Seller Index
        def left_join_seller_index(data_frame):
            data_frame = pd.merge(data_frame, seller_index, how='left', left_on=['Shop ID'], right_on=['Child ShopID'])
            return data_frame

        # 1.4 需要输出的列表
        output_file_list = [['Yesterday', yesterday, yesterday, 'Yesterday New SKUs by KAM'],
                            ['MTD', start_of_this_month, yesterday, 'MTD New SKUs by KAM'],
                            ['M-1', start_of_last_month, end_of_last_month, 'M-1 New SKUs by KAM'],
                            ['WTD', start_of_this_week, yesterday, 'WTD New SKUs by KAM'],
                            ['W-1', start_of_last_week, end_of_last_week, 'W-1 New SKUs by KAM'],
                            ['Cumulative', datetime.date(1900, 1, 1), yesterday, 'Cumulative SKUs by KAM']]

        # 1.5 历遍输出
        for date_period_name, start_date, end_date, file_name in output_file_list:
            new_skus_frame = calculate_num_of_sku(date_period_name, start_date, end_date, file_name, False)
            new_live_skus_frame = calculate_num_of_sku(date_period_name, start_date, end_date, file_name, True)
            merged_df = merge_sku_df(new_skus_frame, new_live_skus_frame)
            # 与Seller Index合并并计算
            merged_df = left_join_seller_index(merged_df)

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

        # 2. 计算New SKUs / New Live SKUs by GP Account + BD Index
        # 2.1 by cat需要输出的列表
        output_file_list = [
            ['Cumulative', datetime.date(1900, 1, 1), yesterday, 'Cumulative SKUs by GP Acc']]

        # 2.2 by cat历遍输出
        for date_period_name, start_date, end_date, file_name in output_file_list:
            new_skus_frame = calculate_num_of_sku(date_period_name, start_date, end_date, file_name, False)
            new_live_skus_frame = calculate_num_of_sku(date_period_name, start_date, end_date, file_name, True)
            merged_df = merge_sku_df(new_skus_frame, new_live_skus_frame)
            # 与Seller Index合并并计算
            merged_df = left_join_seller_index(merged_df)

            # Left Join BD Index
            '''
            bd_index_detail = get_initial_bd_performance_detail()
            merged_df = pd.merge(merged_df, bd_index_detail, how='left',
                                 left_on=['GP Account Name'],
                                 right_on=['Sales Lead: Lead Name'])
            '''

            # 计算OB Team的Avg SKUs
            merged_df = merged_df[(merged_df['Seller Launched by OB?'] == 1)]

            # print(merged_df[:1].unstack())
            merged_df_group = merged_df.groupby([merged_df['Source'], merged_df['Key Brands 1']])
            merged_df_result = merged_df_group.agg({'Cumulative SKUs': 'sum',
                                                    'Cumulative Live SKUs': 'sum'})
            merged_df_result = pd.DataFrame(merged_df_result).reset_index()

            # 输出
            output_file_folder_path = os.path.join(output_file_parent_path, date_period_name)
            output_file_path = os.path.join(output_file_folder_path, file_name + '.csv')
            merged_df_result.to_csv(output_file_path, sep=',', index=False)
            print('%s is completed' % file_name)
            # 上传到BD Performance Report (Daily)
            upload_dataframe_to_google_sheet(merged_df_result
                                             , '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8'
                                             , file_name)

        # 3. 计算Cumulative SKUs by GP acc in different period
        # 3.1 计算Cumulative SKUs by GP acc in different period的函数
        def calculate_num_of_sku_by_gp_acc_in_differnt_period(date_period_name, start_date, end_date, file_name):
            pre_frame = frame[(frame['Date Created'] >= start_date) & (frame['Date Created'] <= end_date)
                              & (frame['Live_status'] == 'live SKUs')]
            column_name = date_period_name + ' Live SKUs'

            # 分组计算
            group = pre_frame['Product ID'].groupby([pre_frame['Shop ID'], pre_frame['Country']])
            output_frame = group.agg({'Product ID': 'count'}) \
                .rename(columns={'Product ID': column_name})
            output_frame = pd.DataFrame(output_frame).reset_index()
            output_frame = output_frame.sort(['Country', column_name]
                                             , ascending=[True, False])

            # 与Seller Index合并并计算
            output_frame = left_join_seller_index(output_frame)

            # 识别GP Acc Created at M-1
            output_frame['GP Acc Created at M-1 Cumulative SKUs'] \
                = np.where(output_frame['GP Acc Created at M-1'] == 1, 0, output_frame[column_name])
            output_frame['GP Acc Created at M-2 Cumulative SKUs'] \
                = np.where(output_frame['GP Acc Created at M-2'] == 1, 0, output_frame[column_name])
            output_frame['GP Acc Created at M-3 Cumulative SKUs'] \
                = np.where(output_frame['GP Acc Created at M-3'] == 1, 0, output_frame[column_name])

            # 分组计算
            group = output_frame.groupby([output_frame['GP Account Owner']])
            output_frame = group.agg({'GP Acc Created at M-1 Cumulative SKUs': 'sum',
                                      'GP Acc Created at M-2 Cumulative SKUs': 'sum',
                                      'GP Acc Created at M-3 Cumulative SKUs': 'sum'})
            output_frame = pd.DataFrame(output_frame).reset_index()
            return output_frame

        # 3.2 需要输出的列表
        output_file_list = [
            ['Cumulative', datetime.date(1900, 1, 1),
             yesterday,
             'Cumulative SKUs by GP Acc in different period']]

        # 3.3 历遍输出
        for date_period_name, start_date, end_date, file_name in output_file_list:
            merged_df = calculate_num_of_sku_by_gp_acc_in_differnt_period(date_period_name,
                                                                          start_date,
                                                                          end_date,
                                                                          file_name)

            output_file_folder_path = os.path.join(output_file_parent_path, date_period_name)
            # 输出
            output_file_path = os.path.join(output_file_folder_path, file_name + '.csv')
            merged_df.to_csv(output_file_path, sep=',', index=False)
            print('%s is completed' % file_name)
            # 上传到BD Performance Report (Daily)
            upload_dataframe_to_google_sheet(merged_df
                                             , '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8'
                                             , file_name)

        # 计算Yesterday
        print('\nCalculating Yesterday Data...')
        output_file_path = output_file_parent_path + "\\Yesterday\\"
        # 计算Yesterday New SKUs
        frame1 = frame[(frame['Date Created'] == yesterday)]
        grouped1 = frame1['Product ID'].groupby(
            [frame1['Seller User ID'], frame1['Shop ID'], frame1['Username'], frame1['Country']])

        Yesterday_New_SKUs_by_Shop = grouped1.agg({'Product ID': {'New SKUs': 'count'}})
        Yesterday_New_SKUs_by_Shop.columns = Yesterday_New_SKUs_by_Shop.columns.droplevel(0)

        Yesterday_New_SKUs_by_Shop.to_csv(output_file_path + 'Yesterday_New_SKUs_by_Shop.csv', sep=',',
                                          encoding='utf-8')

        print('Yesterday_New_SKUs_by_Shop completed')

        # 计算Yesterday New Live SKUs
        frame2 = frame[(frame['Date Created'] == yesterday) & (frame['Status'] == 'Normal')]
        grouped2 = frame2['Product ID'].groupby(
            [frame2['Seller User ID'], frame2['Shop ID'], frame2['Username'], frame2['Country']])

        Yesterday_New_Live_SKUs_by_Shop = grouped2.agg({'Product ID': {'New Live SKUs': 'count'}})
        Yesterday_New_Live_SKUs_by_Shop.columns = Yesterday_New_Live_SKUs_by_Shop.columns.droplevel(0)

        Yesterday_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'Yesterday_New_Live_SKUs_by_Shop.csv', sep=',',
                                               encoding='utf-8')

        print('Yesterday_New_Live_SKUs_by_Shop completed')

        # 计算Cumulative SKUs
        grouped3 = frame['Product ID'].groupby(
            [frame['Seller User ID'], frame['Shop ID'], frame['Username'], frame['Country']])

        Cumulative_SKUs_by_Shop = grouped3.agg({'Product ID': {'Cumulative SKUs': 'count'}})
        Cumulative_SKUs_by_Shop.columns = Cumulative_SKUs_by_Shop.columns.droplevel(0)

        Cumulative_SKUs_by_Shop.to_csv(output_file_path + 'Cumulative_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('Cumulative_SKUs_by_Shop completed')

        # 计算Cumulative Live SKUs
        frame4 = frame.loc[frame['Status'] == 'Normal']
        grouped4 = frame4['Product ID'].groupby(
            [frame4['Seller User ID'], frame4['Shop ID'], frame4['Username'], frame4['Country']])

        Cumulative_Live_SKUs_by_Shop = grouped4.agg({'Product ID': {'Cumulative Live SKUs': 'count'}})
        Cumulative_Live_SKUs_by_Shop.columns = Cumulative_Live_SKUs_by_Shop.columns.droplevel(0)

        Cumulative_Live_SKUs_by_Shop.to_csv(output_file_path + 'Cumulative_Live_SKUs_by_Shop.csv', sep=',',
                                            encoding='utf-8')

        print('Cumulative_Live_SKUs_by_Shop completed')

        # 计算WTD
        print('\nCalculating WTD Data...')
        output_file_path = output_file_parent_path + "\\WTD\\"

        # 计算WTD New SKUs
        frame5 = frame[(frame['Date Created'] >= start_of_this_week) & (frame['Date Created'] <= yesterday)]
        grouped5 = frame5['Product ID'].groupby(
            [frame5['Seller User ID'], frame5['Shop ID'], frame5['Username'], frame5['Country']])

        WTD_New_SKUs_by_Shop = grouped5.agg({'Product ID': {'New SKUs': 'count'}})
        WTD_New_SKUs_by_Shop.columns = WTD_New_SKUs_by_Shop.columns.droplevel(0)

        WTD_New_SKUs_by_Shop.to_csv(output_file_path + 'WTD_New_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('WTD_New_SKUs_by_Shop completed')

        # 计算WTD New Live SKUs
        frame6 = frame[(frame['Date Created'] >= start_of_this_week) & (frame['Date Created'] <= yesterday) & (
            frame['Status'] == 'Normal')]
        grouped6 = frame6['Product ID'].groupby(
            [frame6['Seller User ID'], frame6['Shop ID'], frame6['Username'], frame6['Country']])

        WTD_New_Live_SKUs_by_Shop = grouped6.agg({'Product ID': {'New Live SKUs': 'count'}})
        WTD_New_Live_SKUs_by_Shop.columns = WTD_New_Live_SKUs_by_Shop.columns.droplevel(0)

        WTD_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'WTD_New_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('WTD_New_Live_SKUs_by_Shop completed')

        # 计算W-1
        print('\nCalculating W-1 Data...')
        output_file_path = output_file_parent_path + "\\W-1\\"

        # 计算W-1 New SKUs
        frame7 = frame[(frame['Date Created'] >= start_of_last_week) & (frame['Date Created'] <= end_of_last_week)]
        grouped7 = frame7['Product ID'].groupby(
            [frame7['Seller User ID'], frame7['Shop ID'], frame7['Username'], frame7['Country']])

        W_1_New_SKUs_by_Shop = grouped7.agg({'Product ID': {'New SKUs': 'count'}})
        W_1_New_SKUs_by_Shop.columns = W_1_New_SKUs_by_Shop.columns.droplevel(0)

        W_1_New_SKUs_by_Shop.to_csv(output_file_path + 'W_1_New_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('W_1_New_SKUs_by_Shop completed')

        # 计算W-1 New Live SKUs
        frame8 = frame[(frame['Date Created'] >= start_of_last_week) & (frame['Date Created'] <= end_of_last_week) & (
            frame['Status'] == 'Normal')]
        grouped8 = frame8['Product ID'].groupby(
            [frame8['Seller User ID'], frame8['Shop ID'], frame8['Username'], frame8['Country']])

        W_1_New_Live_SKUs_by_Shop = grouped8.agg({'Product ID': {'New Live SKUs': 'count'}})
        W_1_New_Live_SKUs_by_Shop.columns = W_1_New_Live_SKUs_by_Shop.columns.droplevel(0)

        W_1_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'W_1_New_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('W_1_New_Live_SKUs_by_Shop completed')

        # 计算MTD
        print('\nCalculating MTD Data...')
        output_file_path = output_file_parent_path + "\\MTD\\"

        # 计算MTD New SKUs
        frame9 = frame[(frame['Date Created'] >= start_of_this_month) & (frame['Date Created'] <= yesterday)]
        grouped9 = frame9['Product ID'].groupby(
            [frame9['Seller User ID'], frame9['Shop ID'], frame9['Username'], frame9['Country']])

        MTD_New_SKUs_by_Shop = grouped9.agg({'Product ID': {'New SKUs': 'count'}})
        MTD_New_SKUs_by_Shop.columns = MTD_New_SKUs_by_Shop.columns.droplevel(0)

        MTD_New_SKUs_by_Shop.to_csv(output_file_path + 'MTD_New_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('MTD_New_SKUs_by_Shop completed')

        # 计算MTD New Live SKUs
        frame10 = frame[(frame['Date Created'] >= start_of_this_month) & (frame['Date Created'] <= yesterday) & (
            frame['Status'] == 'Normal')]
        grouped10 = frame10['Product ID'].groupby(
            [frame10['Seller User ID'], frame10['Shop ID'], frame10['Username'], frame10['Country']])

        MTD_New_Live_SKUs_by_Shop = grouped10.agg({'Product ID': {'New Live SKUs': 'count'}})
        MTD_New_Live_SKUs_by_Shop.columns = MTD_New_Live_SKUs_by_Shop.columns.droplevel(0)

        MTD_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'MTD_New_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('MTD_New_Live_SKUs_by_Shop completed')

        # 更新相关表的last update time
        # 更新GP Account Owner Performance Report (Daily)
        upload_last_update_time('1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM', 'Description', 'D5')
        # 更新BD Performance Report (Daily)
        upload_last_update_time('1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8', 'Description', 'D6')

        # 所有步骤执行完后，发一封邮件
        print('\nProcess completed!')
        send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date())
                     + ' SKU by Shop Calculation Completed!', 'SKU Calculation Completed!')


if __name__ == '__main__':
    calculate_sku_by_shop()
