"""
# Period Selection
Yesterday / MTD / M-1 / WTD / W-1

# Calculation
1. order / gmv by shop (done)
2. order / gmv by GP Acc. Owner (done)
3. order / gmv by GP Acc. Owner in different period (done)
4. daily # of orders for the pass 90 days (done)
5. YTD daily order (stop update)
6. MTD daily order by GP Acc. Owner by date
7. kr shops + no GP shops MTD / M-1 daily order (done)

# query_id
994 for monthly performance
990 for weekly performance
1004 for yesterday performance

"""

import logging
import os
import time
import pandas as pd
import numpy as np
from get_redash_query_result import get_shop_performance_by_certain_period, get_fresh_query_result
from get_particular_date import *
from get_google_sheets \
    import upload_dataframe_to_google_sheet, upload_last_update_time, get_certain_google_sheets_to_dataframe
from get_seller_index import get_seller_index_from_google_sheet

# performance by period
# yesterday_performance = get_shop_performance_by_certain_period(1004)
# monthly_performance = get_shop_performance_by_certain_period(994)
# weekly_performance = get_shop_performance_by_certain_period(990)

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# 输出的父目录
output_file_parent_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                          "Shopee 2016.4.12\\2017.2.21 Shop Level Summary"

# seller_index
seller_index = get_seller_index_from_google_sheet()


def calculate_order_performance():
    # 1.1 order_gmv_by_gp_acc_owner_by_country
    order_gmv_by_gp_acc_owner_by_country_list = {'Yesterday':
                                                     [1004, get_yesterday_date(), get_yesterday_date(),
                                                      1, 'Yesterday_Order_GMV_by_KAM'],
                                                 'MTD':
                                                     [994, get_start_of_this_month(), get_yesterday_date(),
                                                      get_mtd_duration(), 'MTD_Order_GMV_by_KAM'],
                                                 'M-1':
                                                     [994, get_start_of_last_month(), get_end_of_last_month(),
                                                      get_last_month_duration(), 'M_1_Order_GMV_by_KAM'],
                                                 'WTD':
                                                     [990, get_this_monday(), get_yesterday_date(), get_wtd_duration(),
                                                      'WTD_Order_GMV_by_KAM'],
                                                 'W-1':
                                                     [990, get_last_monday(), get_last_sunday(), 7,
                                                      'W_1_Order_GMV_by_KAM']
                                                 }

    def calculate_order_gmv_by_gp_acc_owner_by_country(period):
        column_prefix = period.lower()
        # choose query_id
        query_id = order_gmv_by_gp_acc_owner_by_country_list[period][0]
        # get date_range to calculate daily figures
        date_range = order_gmv_by_gp_acc_owner_by_country_list[period][3]

        performance_data = get_shop_performance_by_certain_period(query_id)

        performance_data_group = performance_data.groupby([performance_data['GP Account Owner'],
                                                           performance_data['country']])
        performance_data_result = performance_data_group.agg({column_prefix + '_gross_orders': 'sum',
                                                              column_prefix + '_gmv_usd': 'sum'}).reset_index()

        # daily average
        performance_data_result[column_prefix + '_daily_gross_orders'] \
            = performance_data_result[column_prefix + '_gross_orders'] / date_range
        performance_data_result[column_prefix + '_daily_gmv_usd'] \
            = performance_data_result[column_prefix + '_gmv_usd'] / date_range

        # abs
        performance_data_result['ABS'] \
            = performance_data_result[column_prefix + '_gmv_usd'] / performance_data_result[
            column_prefix + '_gross_orders']

        # empty column
        performance_data_result[column_prefix + '_net_orders'] = None
        performance_data_result[column_prefix + '_nmv_usd'] = None

        # sort columns
        column_sort = ['GP Account Owner',
                       'country',
                       column_prefix + '_gross_orders',
                       column_prefix + '_net_orders',
                       column_prefix + '_gmv_usd',
                       column_prefix + '_nmv_usd',
                       'ABS',
                       column_prefix + '_daily_gross_orders',
                       column_prefix + '_daily_gmv_usd']

        performance_data_result = performance_data_result[column_sort]

        logging.info('Calculation for ' + period + ' order/gmv by gp acc. owner by country is completed.')

        # upload to google sheet
        google_sheet_id = '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
        google_sheet_name = order_gmv_by_gp_acc_owner_by_country_list[period][4]

        logging.info('Start to upload ' + google_sheet_name + ' to google sheet.')
        upload_dataframe_to_google_sheet(performance_data_result,
                                         google_sheet_id,
                                         google_sheet_name)

        logging.info(google_sheet_name + ' is uploaded to google sheet.')

        # export to folder
        file_name = order_gmv_by_gp_acc_owner_by_country_list[period][4] + '.csv'
        file_path = os.path.join(output_file_parent_path, period, file_name)

        logging.info('Start to export ' + file_name + ' to folder.')
        performance_data_result.to_csv(file_path, sep=',')
        logging.info(file_name + ' is exported to folder.')

        return performance_data_result

    # 2.1 order_gmv_by_gp_acc_owner
    order_gmv_by_gp_acc_owner_list = {'MTD':
                                          [994, get_start_of_this_month(), get_yesterday_date(),
                                           get_mtd_duration(), 'MTD_Order_GMV_by_KAM_Overall'],
                                      'M-1':
                                          [994, get_start_of_last_month(), get_end_of_last_month(),
                                           get_last_month_duration(), 'M_1_Order_GMV_by_KAM_Overall'],
                                      }

    def calculate_order_gmv_by_gp_acc_owner(period):
        column_prefix = period.lower()
        # choose query_id
        query_id = order_gmv_by_gp_acc_owner_list[period][0]
        # get date_range to calculate daily figures
        date_range = order_gmv_by_gp_acc_owner_list[period][3]

        performance_data = get_shop_performance_by_certain_period(query_id)
        performance_data_group = performance_data.groupby([performance_data['GP Account Owner']])
        performance_data_result = performance_data_group.agg({column_prefix + '_gross_orders': 'sum',
                                                              column_prefix + '_gmv_usd': 'sum'}).reset_index()

        # daily average
        performance_data_result[column_prefix + '_daily_gross_orders'] \
            = performance_data_result[column_prefix + '_gross_orders'] / date_range
        performance_data_result[column_prefix + '_daily_gmv_usd'] \
            = performance_data_result[column_prefix + '_gmv_usd'] / date_range

        # abs
        performance_data_result['ABS'] \
            = performance_data_result[column_prefix + '_gmv_usd'] / performance_data_result[
            column_prefix + '_gross_orders']

        # empty column
        performance_data_result[column_prefix + '_net_orders'] = None
        performance_data_result[column_prefix + '_nmv_usd'] = None

        # sort columns
        column_sort = ['GP Account Owner',
                       column_prefix + '_gross_orders',
                       column_prefix + '_net_orders',
                       column_prefix + '_gmv_usd',
                       column_prefix + '_nmv_usd',
                       'ABS',
                       column_prefix + '_daily_gross_orders',
                       column_prefix + '_daily_gmv_usd']

        performance_data_result = performance_data_result[column_sort]

        performance_data_result = performance_data_result.sort_values(by=[column_prefix + '_daily_gross_orders'],
                                                                      ascending=[False])

        logging.info('Calculation for ' + period + ' order/gmv by gp acc. owner is completed.')

        # upload to google sheet
        google_sheet_id = '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
        google_sheet_name = order_gmv_by_gp_acc_owner_list[period][4]

        logging.info('Start to upload ' + google_sheet_name + ' to google sheet.')
        upload_dataframe_to_google_sheet(performance_data_result,
                                         google_sheet_id,
                                         google_sheet_name)

        logging.info(google_sheet_name + ' is uploaded to google sheet.')

        return performance_data_result

    # 3.1 90_days_order_for_each_country
    def calculate_90_days_order_for_each_country():
        get_90_days_order_for_each_country = get_fresh_query_result('http://10.12.5.53',
                                                                    1200,
                                                                    'PrsLn6Mf09MuBxBTrAEeRdT3gyqKzbG20obScoEV',
                                                                    {})

        get_90_days_order_for_each_country = pd.pivot_table(get_90_days_order_for_each_country,
                                                            index=['date_id'],
                                                            values='cb_order',
                                                            columns='country',
                                                            aggfunc=np.sum).reset_index().rename_axis(None, axis=1)

        # upload to google sheet
        google_sheet_id = '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
        google_sheet_name = 'D-90 Order by Country'

        logging.info('Start to upload ' + google_sheet_name + ' to google sheet.')
        upload_dataframe_to_google_sheet(get_90_days_order_for_each_country,
                                         google_sheet_id,
                                         google_sheet_name)

    # 4.1 order_by_gp_acc_in_different_stage
    order_by_gp_acc_in_different_stage_list = {'MTD':
                                                   [994, get_start_of_this_month(), get_yesterday_date(),
                                                    get_mtd_duration(), 'MTD_Order_by_GP_Acc_in_different_stage']}

    def calculate_order_by_gp_acc_in_different_stage(period):
        column_prefix = period.lower()
        # choose query_id
        query_id = order_by_gp_acc_in_different_stage_list[period][0]
        # get date_range to calculate daily figures
        date_range = order_by_gp_acc_in_different_stage_list[period][3]
        # three stage
        stage_list = ['GP Acc Created at M-1',
                      'GP Acc Created at M-2',
                      'GP Acc Created at M-3']

        performance_data = get_shop_performance_by_certain_period(query_id)

        performance_data_group = performance_data.groupby([performance_data['GP Account Owner'],
                                                           performance_data[stage_list[0]],
                                                           performance_data[stage_list[1]],
                                                           performance_data[stage_list[2]]])
        performance_data_result = performance_data_group.agg({column_prefix + '_gross_orders': 'sum'}).reset_index()

        for index, stage in enumerate(stage_list):
            stage_result = performance_data_result[['GP Account Owner',
                                                    stage,
                                                    column_prefix + '_gross_orders']] \
                .rename(columns={column_prefix + '_gross_orders': stage + ' Gross Order'})
            stage_result = stage_result[stage_result[stage] == 1]
            stage_result = stage_result[['GP Account Owner', stage + ' Gross Order']]

            if index == 0:
                concat_result = stage_result
            else:
                concat_result = pd.merge(concat_result, stage_result, how='outer',
                                         left_on=['GP Account Owner'], right_on=['GP Account Owner'])

        for index, stage in enumerate(stage_list):
            concat_result[stage + ' Daily Gross Order'] = concat_result[stage + ' Gross Order'] / date_range

        concat_result = concat_result.fillna(0)

        logging.info('Calculation for ' + period + ' order_by_gp_acc_in_different_stage is completed.')

        # upload to google sheet
        google_sheet_id = '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8'
        google_sheet_name = order_by_gp_acc_in_different_stage_list[period][4]

        logging.info('Start to upload ' + google_sheet_name + ' to google sheet.')
        upload_dataframe_to_google_sheet(concat_result,
                                         google_sheet_id,
                                         google_sheet_name)

        logging.info(google_sheet_name + ' is uploaded to google sheet.')

        return concat_result

    # 5.1 order_gmv_by_shop
    order_gmv_by_shop_list = {'Yesterday':
                                  [1004, get_yesterday_date(), get_yesterday_date(),
                                   1, 'Yesterday_Order_GMV_by_Shop'],
                              'MTD':
                                  [994, get_start_of_this_month(), get_yesterday_date(),
                                   get_mtd_duration(), 'MTD_Order_GMV_by_Shop'],
                              'M-1':
                                  [994, get_start_of_last_month(), get_end_of_last_month(),
                                   get_last_month_duration(), 'M_1_Order_GMV_by_Shop'],
                              'WTD':
                                  [990, get_this_monday(), get_yesterday_date(), get_wtd_duration(),
                                   'WTD_Order_GMV_by_Shop'],
                              'W-1':
                                  [990, get_last_monday(), get_last_sunday(), 7,
                                   'W_1_Order_GMV_by_Shop']
                              }

    def calculate_order_gmv_by_shop(period):
        column_prefix = period.lower()
        # choose query_id
        query_id = order_gmv_by_shop_list[period][0]
        # get date_range to calculate daily figures
        date_range = order_gmv_by_shop_list[period][3]

        performance_data = get_shop_performance_by_certain_period(query_id)

        performance_data_group = performance_data.groupby([performance_data['Child UserID'],
                                                           performance_data['Child ShopID'],
                                                           performance_data['Child Account Name'],
                                                           performance_data['country']])
        performance_data_result = performance_data_group.agg({column_prefix + '_gross_orders': 'sum',
                                                              column_prefix + '_gmv_usd': 'sum'}).reset_index()

        # daily average
        performance_data_result[column_prefix + '_daily_gross_orders'] \
            = performance_data_result[column_prefix + '_gross_orders'] / date_range
        performance_data_result[column_prefix + '_daily_gmv_usd'] \
            = performance_data_result[column_prefix + '_gmv_usd'] / date_range

        # abs
        performance_data_result['ABS'] \
            = performance_data_result[column_prefix + '_gmv_usd'] / performance_data_result[
            column_prefix + '_gross_orders']

        # empty column
        performance_data_result[column_prefix + '_net_orders'] = None
        performance_data_result[column_prefix + '_nmv_usd'] = None

        # sort columns
        column_sort = ['Child UserID',
                       'Child ShopID',
                       'Child Account Name',
                       'country',
                       column_prefix + '_gross_orders',
                       column_prefix + '_net_orders',
                       column_prefix + '_gmv_usd',
                       column_prefix + '_nmv_usd',
                       'ABS',
                       column_prefix + '_daily_gross_orders',
                       column_prefix + '_daily_gmv_usd']

        performance_data_result = performance_data_result[column_sort]

        logging.info('Calculation for ' + period + ' order/gmv by shop is completed.')

        # export to folder
        file_name = order_gmv_by_shop_list[period][4] + '.csv'
        file_path = os.path.join(output_file_parent_path, period, file_name)

        logging.info('Start to export ' + file_name + ' to folder.')
        performance_data_result.to_csv(file_path, sep=',')
        logging.info(file_name + ' is exported to folder.')

        return performance_data_result

    # 6.1 kr_shop_and_non_gp_shop_mtd_m-1_ado
    def calculate_kr_shop_and_non_gp_shop_mtd_m_1_ado():
        kr_shop_list = get_certain_google_sheets_to_dataframe('GP Account Owner Performance Report (Daily)',
                                                              'KR Shop List')

        no_gp_shop_list = seller_index[seller_index['GP Account Owner'].isnull()]
        no_gp_shop_list = no_gp_shop_list[['Child ShopID', 'Child Account Name']] \
            .rename(columns={'Child ShopID': 'ShopID', 'Child Account Name': 'Shopname'})

        tiger_wong_shop_list = seller_index[seller_index['GP Account Owner'] == 'Tiger Wong']
        tiger_wong_shop_list = tiger_wong_shop_list[['Child ShopID', 'Child Account Name']] \
            .rename(columns={'Child ShopID': 'ShopID', 'Child Account Name': 'Shopname'})

        all_list_frame = [kr_shop_list, no_gp_shop_list, tiger_wong_shop_list]
        all_list = pd.concat(all_list_frame)

        # 获取GP Account Owner
        all_list = pd.merge(all_list, seller_index, how='left', left_on=['ShopID'], right_on=['Child ShopID'])

        mtd_ado_by_shop_path = os.path.join(output_file_parent_path, "MTD", "MTD_Order_GMV_by_Shop.csv")
        m_1_ado_by_shop_path = os.path.join(output_file_parent_path, "M-1", "M_1_Order_GMV_by_Shop.csv")

        pwd = os.getcwd()
        os.chdir(os.path.dirname(mtd_ado_by_shop_path))
        mtd_ado_by_shop = pd.read_csv(os.path.basename(mtd_ado_by_shop_path), sep=',', encoding='ISO-8859-1')
        os.chdir(pwd)

        pwd = os.getcwd()
        os.chdir(os.path.dirname(m_1_ado_by_shop_path))
        m_1_ado_by_shop = pd.read_csv(os.path.basename(m_1_ado_by_shop_path), sep=',', encoding='ISO-8859-1')
        os.chdir(pwd)

        all_list = pd.merge(all_list, mtd_ado_by_shop, how='left', left_on=['ShopID'], right_on=['Child ShopID'])
        all_list = pd.merge(all_list, m_1_ado_by_shop, how='left', left_on=['ShopID'], right_on=['Child ShopID'])

        all_list = all_list[['ShopID', 'Shopname', 'mtd_daily_gross_orders',
                             'm-1_daily_gross_orders', 'GP Account Owner',
                             'Child Account Record Type - Country']]

        # 去重
        all_list = all_list.drop_duplicates()

        # 去除nan
        all_list = all_list.fillna(0)

        logging.info('Calculation for kr_shop_and_non_gp_shop_mtd_m_1_ado is completed.')

        upload_dataframe_to_google_sheet(all_list, '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM', 'Excluded Shops ADO')

    # 7.1 mtd_daily_order_by_gp_acc_owner_by_country
    def calculate_mtd_daily_order_by_gp_acc_owner_by_country():
        country_list = ['sg', 'my', 'tw', 'id', 'th', 'ph', 'vn']
        start_date = get_start_of_this_month().strftime('%Y-%m-%d')
        end_date = get_yesterday_date().strftime('%Y-%m-%d')

        execute_success = None

        while execute_success is None:
            try:
                for index, country in enumerate(country_list):
                    params = {'p_country': country,
                              'p_start_date': start_date,
                              'p_end_date': end_date}

                    get_MTD_daily_order_by_gp_acc_owner_by_country \
                        = get_fresh_query_result('http://10.12.5.53',
                                                 1269,
                                                 'PrsLn6Mf09MuBxBTrAEeRdT3gyqKzbG20obScoEV',
                                                 params)

                    if index == 0:
                        final_result = get_MTD_daily_order_by_gp_acc_owner_by_country
                    else:
                        final_result = final_result.append(get_MTD_daily_order_by_gp_acc_owner_by_country)
                execute_success = 1
            except Exception as err:
                logging.info('An exception occurred: ' + str(err) + ', try again.')
                time.sleep(60)
                pass

        final_result = pd.pivot_table(final_result, values=['count'],
                                      index=['GP Account Owner', 'country'], columns=['date_id'], aggfunc='sum') \
            .reset_index()

        final_result.columns = final_result.columns.droplevel(0)

        # 补充两列列名，不然上传会报错
        final_result.columns.values[0] = 'GP Account Owner'
        final_result.columns.values[1] = 'Country'

        final_result = final_result.fillna(0)

        # upload to google sheet
        google_sheet_id = '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
        google_sheet_name = 'MTD Daily Gross Order by GP Acc Owner'

        logging.info('Start to upload ' + google_sheet_name + ' to google sheet.')
        upload_dataframe_to_google_sheet(final_result,
                                         google_sheet_id,
                                         google_sheet_name)

        logging.info(google_sheet_name + ' is uploaded to google sheet.')

        return final_result

    # 1.2 calculate_order_gmv_by_gp_acc_owner_by_country
    for key, value in order_gmv_by_gp_acc_owner_by_country_list.items():
        calculate_order_gmv_by_gp_acc_owner_by_country(key)

    # 2.2 calculate_order_gmv_by_gp_acc_owner
    for key, value in order_gmv_by_gp_acc_owner_list.items():
        calculate_order_gmv_by_gp_acc_owner(key)

    # 3.2 calculate_90_days_order_for_each_country
    calculate_90_days_order_for_each_country()

    # 4.2 calculate_order_by_gp_acc_in_different_stage
    for key, value in order_by_gp_acc_in_different_stage_list.items():
        calculate_order_by_gp_acc_in_different_stage(key)

    # 5.2 calculate_order_gmv_by_shop
    for key, value in order_gmv_by_shop_list.items():
        calculate_order_gmv_by_shop(key)

    # 6.2 calculate_kr_shop_and_non_gp_shop_mtd_m-1_ado
    calculate_kr_shop_and_non_gp_shop_mtd_m_1_ado()

    # 7.2 calculate_mtd_daily_order_by_gp_acc_owner_by_country
    calculate_mtd_daily_order_by_gp_acc_owner_by_country()

    # 更新GP Account Owner Performance Report (Daily)
    upload_last_update_time('1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM', 'Description', 'D4')
    # 更新BD Performance Report (Daily)
    upload_last_update_time('1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8', 'Description', 'D5')


if __name__ == '__main__':
    calculate_order_performance()
