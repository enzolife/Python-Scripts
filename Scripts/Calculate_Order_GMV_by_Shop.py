# coding: utf-8
import pandas as pd
import numpy as np
from get_particular_date import *
from get_order_report import get_concatenated_order_report
from get_local_currency import get_local_currency
from get_gmail_config import *
from get_google_sheets import *
from get_seller_index import get_seller_index_from_google_sheet


def calculate_order_gmv_by_shop():
    # Order Report的目录
    # input_file_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
    # 'Shopee 2016.4.12\\2016.4.23 Data Visualization\\Order'
    # 获取concatenated order report
    frame = get_concatenated_order_report()
    print('orders reports are concatenating.\n')
    # 输出的父目录
    output_file_parent_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                              "Shopee 2016.4.12\\2017.2.21 Shop Level Summary"

    # 输出csv函数
    def export_csv_to_certain_path(dataframe_name, file_name, folder_name):
        dataframe_name.to_csv(output_file_parent_path + '\\' + folder_name + '\\' + file_name + '.csv', sep=',',
                              encoding='utf-8')
        print(file_name + ' completed!')

    # 如果合并frame存在
    if frame is not False:

        # 确认日期没错
        print('Yesterday is: ' + get_yesterday_date().strftime("%Y-%m-%d")
              + ', Now calculating order gmv by shop result.')
        # 转换Purchased on的格式
        frame['Purchased on'] = pd.to_datetime(frame['Purchased on'])
        frame['Purchased on (Y/m)'] = frame['Purchased on'].dt.strftime('%Y/%m')
        frame['Purchased on (Y/m/d)'] = frame['Purchased on'].dt.strftime('%Y/%m/%d')
        # left join Currency List
        currency_list = get_local_currency()
        frame = pd.merge(frame, currency_list, how='left', left_on=['Country'], right_on=['currency_name'])
        # left join Seller Index
        seller_index = get_seller_index_from_google_sheet()
        frame = pd.merge(frame, seller_index, how='left', left_on=['ShopId(S)'], right_on=['Child ShopID'])
        # 计算GMV in USD
        frame['GMV in USD'] = (frame['Grand Total'] / frame['Currency']).apply(pd.to_numeric)
        # 尝试识别Net Order, NMV
        frame['Net Order'] = np.where(frame['Status(FE)'] == 'Cancelled', 0, 1)
        frame['NMV'] = np.where(frame['Status(FE)'] == 'Cancelled', 0, frame['GMV in USD'])
        # 添加周数
        frame['Week Num'] = frame['Purchased on'].dt.week
        # 添加年份
        frame['Year'] = frame['Purchased on'].dt.year
        # 添加昨天
        frame['Yesterday Date'] = get_yesterday_date()
        # 添加Purchased on M-1/M-2/M-3
        i = 1
        while i <= 3:
            frame['Purchased on at M-' + str(i)] = np.where(
                (frame['Purchased on']
                 <= get_start_end_of_certain_month(i, 'end')) & (
                    frame['Purchased on']
                    >= get_start_end_of_certain_month(i, 'start')), 1, 0)
            i = i + 1
        frame[:50].to_csv("D://order.csv", sep=',', encoding='utf-8')

        # 1. 计算Order/GMV Daily
        # 1.1 计算Order/GMV Daily的序列
        output_file_list = [['Yesterday', get_yesterday_date(), get_yesterday_date(),
                             1, 'Yesterday_Order_GMV_by_Shop'],
                            ['MTD', get_start_of_this_month(), get_yesterday_date(),
                             get_mtd_duration(), 'MTD_Order_GMV_by_Shop'],
                            ['M-1', get_start_of_last_month(), get_end_of_last_month(),
                             get_last_month_duration(), 'M_1_Order_GMV_by_Shop'],
                            ['WTD', get_this_monday(), get_yesterday_date(),
                             get_wtd_duration(), 'WTD_Order_GMV_by_Shop'],
                            ['W-1', get_last_monday(), get_last_sunday(),
                             7, 'W_1_Order_GMV_by_Shop']]

        # 1.2 计算Order/GMV Daily by different period的函数
        def calculate_order_gmv_by_shop_by_period(date_period_name, start_date, end_date, duration_of_period,
                                                  file_name):
            filtered_frame = frame[(frame['Purchased on'] >= start_date) & (frame['Purchased on'] <= end_date)]
            filtered_group = filtered_frame.groupby([filtered_frame['Seller User ID'], filtered_frame['ShopId(S)'],
                                                     filtered_frame['Username(S)'], filtered_frame['Country']])
            filtered_result = filtered_group.agg({'Order ID': 'count',
                                                  'Net Order': 'sum',
                                                  'GMV in USD': 'sum',
                                                  'NMV': 'sum'}) \
                .rename(columns={'Order ID': 'Gross Order',
                                 'GMV in USD': 'GMV USD',
                                 'NMV': 'NMV USD'})
            filtered_result['ABS'] = filtered_result['GMV USD'] / filtered_result['Gross Order']
            filtered_result['Daily Gross Order'] = filtered_result['Gross Order'] / duration_of_period
            filtered_result['Daily GMV USD'] = filtered_result['GMV USD'] / duration_of_period
            filtered_result = pd.DataFrame(filtered_result).reset_index()
            # 输出csv
            export_csv_to_certain_path(filtered_result, file_name, date_period_name)
            # 上传google sheet
            # upload_dataframe_to_google_sheet(filtered_result
            # , '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
            # , file_name)

        # 1.3 开始历遍
        for date_period_name, start_date, end_date, duration_of_period, file_name in output_file_list:
            calculate_order_gmv_by_shop_by_period(date_period_name, start_date, end_date, duration_of_period, file_name)

        # 2. 计算Order/GMV Daily by Country by KAM by different period
        # 2.1 计算Order/GMV Daily by Country by KAM by different period的序列
        output_file_list = [['Yesterday', get_yesterday_date(), get_yesterday_date(),
                             1, 'Yesterday_Order_GMV_by_KAM'],
                            ['MTD', get_start_of_this_month(), get_yesterday_date(),
                             get_mtd_duration(), 'MTD_Order_GMV_by_KAM'],
                            ['M-1', get_start_of_last_month(), get_end_of_last_month(),
                             get_last_month_duration(), 'M_1_Order_GMV_by_KAM'],
                            ['WTD', get_this_monday(), get_yesterday_date(),
                             get_wtd_duration(), 'WTD_Order_GMV_by_KAM'],
                            ['W-1', get_last_monday(), get_last_sunday(),
                             7, 'W_1_Order_GMV_by_KAM']]

        # 2.2 计算Order/GMV Daily by Country by KAM by different period的函数
        def calculate_order_gmv_by_country_by_kam_by_period(date_period_name, start_date, end_date, duration_of_period, file_name):
            filtered_frame = frame[(frame['Purchased on'] >= start_date) & (frame['Purchased on'] <= end_date)]
            filtered_group = filtered_frame.groupby([filtered_frame['GP Account Owner'], filtered_frame['Country']])
            filtered_result = filtered_group.agg({'Order ID': 'count',
                                                  'Net Order': 'sum',
                                                  'GMV in USD': 'sum',
                                                  'NMV': 'sum'}) \
                .rename(columns={'Order ID': 'Gross Order',
                                 'GMV in USD': 'GMV USD',
                                 'NMV': 'NMV USD'})
            filtered_result['ABS'] = filtered_result['GMV USD'] / filtered_result['Gross Order']
            filtered_result['Daily Gross Order'] = filtered_result['Gross Order'] / duration_of_period
            filtered_result['Daily GMV USD'] = filtered_result['GMV USD'] / duration_of_period
            filtered_result = pd.DataFrame(filtered_result).reset_index()
            # 输出csv
            export_csv_to_certain_path(filtered_result, file_name, date_period_name)
            # 上传GP Account Owner Performance Report (Daily)
            upload_dataframe_to_google_sheet(filtered_result
                                             , '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
                                             , file_name)

        # 2.3 开始历遍
        for date_period_name, start_date, end_date, duration_of_period, file_name in output_file_list:
            calculate_order_gmv_by_country_by_kam_by_period(date_period_name, start_date, end_date, duration_of_period, file_name)

        # 3. 计算Order/GMV Daily by KAM by different period
        # 3.1 计算Order/GMV Daily by KAM by different period的序列
        output_file_list = [['MTD', get_start_of_this_month(), get_yesterday_date(),
                             get_mtd_duration(), 'MTD_Order_GMV_by_KAM_Overall'],
                            ['M-1', get_start_of_last_month(), get_end_of_last_month(),
                             get_last_month_duration(), 'M_1_Order_GMV_by_KAM_Overall']]

        # 3.2 计算Order/GMV Daily by KAM by different period的函数
        def calculate_order_gmv_by_kam_by_period(date_period_name, start_date, end_date, duration_of_period, file_name):
            filtered_frame = frame[(frame['Purchased on'] >= start_date) & (frame['Purchased on'] <= end_date)]
            filtered_group = filtered_frame.groupby([filtered_frame['GP Account Owner']])
            filtered_result = filtered_group.agg({'Order ID': 'count',
                                                  'Net Order': 'sum',
                                                  'GMV in USD': 'sum',
                                                  'NMV': 'sum'}) \
                .rename(columns={'Order ID': 'Gross Order',
                                 'GMV in USD': 'GMV USD',
                                 'NMV': 'NMV USD'})
            filtered_result['ABS'] = filtered_result['GMV USD'] / filtered_result['Gross Order']
            filtered_result['Daily Gross Order'] = filtered_result['Gross Order'] / duration_of_period
            filtered_result['Daily GMV USD'] = filtered_result['GMV USD'] / duration_of_period
            filtered_result = pd.DataFrame(filtered_result).reset_index()
            filtered_result = filtered_result.sort('Daily Gross Order', ascending=False)
            # 输出csv
            export_csv_to_certain_path(filtered_result, file_name, date_period_name)
            # 上传GP Account Owner Performance Report (Daily)
            upload_dataframe_to_google_sheet(filtered_result
                                             , '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
                                             , file_name)

        # 3.3 开始历遍
        for date_period_name, start_date, end_date, duration_of_period, file_name in output_file_list:
            calculate_order_gmv_by_kam_by_period(date_period_name, start_date, end_date, duration_of_period, file_name)

        # 4. 计算上线30天/60天/90天的MTD/M-1 Order by GP Acc
        # 4.1 计算上线30天/60天/90天的MTD/M-1 Order by GP Acc的序列
        output_file_list = [['MTD', get_start_of_this_month(), get_yesterday_date(),
                             get_mtd_duration(), 'MTD_Order_by_GP_Acc_in_different_stage']]

        # 4.2 计算上线30天/60天/90天的MTD/M-1 Order by GP Acc的函数
        def calculate_order_by_gp_acc_in_different_stage(date_period_name,
                                                         start_date,
                                                         end_date,
                                                         duration_of_period,
                                                         file_name):
            filtered_frame = frame[(frame['Purchased on'] >= start_date) & (frame['Purchased on'] <= end_date)]
            filtered_group = filtered_frame.groupby([filtered_frame['GP Account Owner']])
            filtered_result = filtered_group.agg({'GP Acc Created at M-1': 'sum',
                                                  'GP Acc Created at M-2': 'sum',
                                                  'GP Acc Created at M-3': 'sum'}) \
                .rename(columns={'GP Acc Created at M-1': 'GP Acc Created at M-1 Gross Order',
                                 'GP Acc Created at M-2': 'GP Acc Created at M-2 Gross Order',
                                 'GP Acc Created at M-3': 'GP Acc Created at M-3 Gross Order'})

            filtered_result['GP Acc Created at M-1 Daily Gross Order']\
                = filtered_result['GP Acc Created at M-1 Gross Order'] / duration_of_period
            filtered_result['GP Acc Created at M-2 Daily Gross Order'] \
                = filtered_result['GP Acc Created at M-2 Gross Order'] / duration_of_period
            filtered_result['GP Acc Created at M-3 Daily Gross Order'] \
                = filtered_result['GP Acc Created at M-3 Gross Order'] / duration_of_period
            filtered_result = pd.DataFrame(filtered_result).reset_index()
            # 输出csv
            export_csv_to_certain_path(filtered_result, file_name, date_period_name)
            # 上传GP Account Owner Performance Report (Daily)
            upload_dataframe_to_google_sheet(filtered_result
                                             , '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8'
                                             , file_name)

        # 4.3 开始历遍
        for date_period_name, start_date, end_date, duration_of_period, file_name in output_file_list:
            calculate_order_by_gp_acc_in_different_stage(date_period_name,
                                                         start_date,
                                                         end_date,
                                                         duration_of_period,
                                                         file_name)

        # 5. 计算W-1/2/3/4/5 Order&Daily Order by Shops
        current_week_num = get_current_week_num()
        current_year = get_current_year()
        five_weeks_before = current_week_num - 5
        frame6 = frame[(frame['Week Num'] >= five_weeks_before)
                       & (frame['Week Num'] < 52)
                       & (frame['Year'] == current_year)]
        grouped6 = frame6.groupby([frame6['GP Account Owner'],
                                   frame6['Seller User ID'],
                                   frame6['ShopId(S)'],
                                   frame6['Username(S)'],
                                   frame6['Shopee Account Created Date'],
                                   frame6['Country'],
                                   frame6['Week Num']])
        result6 = grouped6.agg({'Order ID': 'count'}) \
            .rename(columns={'Order ID': 'Gross Order'})
        result6 = result6.unstack('Week Num')
        result6.columns = result6.columns.droplevel(0)
        export_csv_to_certain_path(result6, 'Last_5_Weeks_Order_by_Shop', 'Cumulative')

        # 6. 计算90天Order数
        frame7 = frame[(frame['Purchased on'] >= get_yesterday_date() + datetime.timedelta(days=-90))]
        grouped7 = frame7.groupby([frame7['Purchased on'], frame7['Country']])
        result7 = grouped7.agg({'Order ID': 'count'}).rename(columns={'Order ID': 'Gross Order'})
        result7 = result7.unstack('Country')
        result7.columns = result7.columns.droplevel(0)
        export_csv_to_certain_path(result7, 'D-90 Order by Country', 'Cumulative')
        # 上传GP Account Owner Performance Report (Daily)
        upload_dataframe_to_google_sheet(result7
                                         , '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
                                         , 'D-90 Order by Country')

        # 7. 计算YTD Daily Order
        YTD_Daily_Order_List = ['SG', 'MY', 'TW', 'ID', 'TH']

        for country_name in YTD_Daily_Order_List:
            ytd_daily_order_pre_frame = frame[(frame['Purchased on'] >= datetime.date(2017, 1, 1))
                                              & (frame['Country'] == country_name)]
            ytd_daily_order_group = ytd_daily_order_pre_frame.groupby(
                [ytd_daily_order_pre_frame['Purchased on (Y/m/d)']])
            ytd_daily_order_frame = ytd_daily_order_group.agg({'Order ID': 'count'}) \
                .rename(columns={'Order ID': 'CB Gross Order'})
            # 上传到Order Performance by Country, Daily, YTD
            upload_dataframe_to_google_sheet(ytd_daily_order_frame,
                                             '19t8cG1FhuZsQ961fk58bUqf3lkd29kto_sGR0595QZI',
                                             country_name + '-CB')

        # 8. 计算MTD Daily Order by GP Acc
        def calculate_mtd_order_by_country_by_gp_acc(date_period_name,
                                                     start_date,
                                                     end_date,
                                                     duration_of_period,
                                                     file_name):
            filtered_frame = frame[(frame['Purchased on'] >= start_date) & (frame['Purchased on'] <= end_date)]
            filtered_group = filtered_frame.groupby([filtered_frame['GP Account Owner'],
                                                     filtered_frame['Country'],
                                                     filtered_frame['Purchased on']])
            filtered_result = filtered_group.agg({'Order ID': 'count'}) \
                .rename(columns={'Order ID': 'Gross Order'})
            filtered_result = pd.DataFrame(filtered_result).unstack().reset_index()
            filtered_result.columns = filtered_result.columns.droplevel(0)
            # 补充两列列名，不然上传会报错
            filtered_result.columns.values[0] = 'GP Account Owner'
            filtered_result.columns.values[1] = 'Country'
            # 输出csv
            export_csv_to_certain_path(filtered_result, file_name, date_period_name)
            # 上传GP Account Owner Performance Report (Daily)
            upload_dataframe_to_google_sheet(filtered_result
                                             , '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
                                             , file_name)

        calculate_mtd_order_by_country_by_gp_acc('MTD',
                                                 get_start_of_this_month(),
                                                 get_yesterday_date(),
                                                 get_mtd_duration(),
                                                 'MTD Daily Gross Order by GP Acc Owner')

        # 9. 计算MTD Daily Order by Shops

        # 10. 计算MTD/M-1 Order by GP Acc

        # 11. 计算KR MTD/M-1 Order by Shop + 没有GP Link的MTD/M-1 Order by Shop
        kr_shop_list = get_certain_google_sheets_to_dataframe('GP Account Owner Performance Report (Daily)',
                                                              'KR Shop List')

        no_gp_shop_list = seller_index[seller_index['GP Account Owner ID'] == np.NAN]
        no_gp_shop_list = no_gp_shop_list[['Child ShopID', 'Child Account Name']]\
            .rename(columns={'Child ShopID': 'ShopID', 'Child Account Name': 'Shopname'})

        all_list_frame = [kr_shop_list, no_gp_shop_list]
        all_list = pd.concat(all_list_frame)

        mtd_ado_by_shop_path = os.path.join(output_file_parent_path, "MTD", "MTD_Order_GMV_by_Shop.csv")
        m_1_ado_by_shop_path = os.path.join(output_file_parent_path, "M-1", "M_1_Order_GMV_by_Shop.csv")

        pwd = os.getcwd()
        os.chdir(os.path.dirname(mtd_ado_by_shop_path))
        mtd_ado_by_shop = pd.read_csv(os.path.basename(mtd_ado_by_shop_path), sep=',')
        os.chdir(pwd)

        pwd = os.getcwd()
        os.chdir(os.path.dirname(m_1_ado_by_shop_path))
        m_1_ado_by_shop = pd.read_csv(os.path.basename(m_1_ado_by_shop_path), sep=',')
        os.chdir(pwd)

        all_list = pd.merge(all_list, mtd_ado_by_shop, how='left', left_on=['ShopID'], right_on=['ShopId(S)'])
        all_list = pd.merge(all_list, m_1_ado_by_shop, how='left', left_on=['ShopID'], right_on=['ShopId(S)'])

        all_list = all_list[['ShopID', 'Shopname', 'Daily Gross Order_x', 'Daily Gross Order_y']]

        upload_dataframe_to_google_sheet(all_list, '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM', 'Excluded Shops ADO')

        # 更新相关表的last update time
        # 更新GP Account Owner Performance Report (Daily)
        upload_last_update_time('1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM', 'Description', 'D4')
        # 更新BD Performance Report (Daily)
        upload_last_update_time('1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8', 'Description', 'D5')

        # 所有步骤执行完后
        print('\nProcess completed!')
        send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date()) +
                     ' Order GMV by Shop Calculation Completed!', 'Order Calculation Completed!')


if __name__ == '__main__':
    calculate_order_gmv_by_shop()
