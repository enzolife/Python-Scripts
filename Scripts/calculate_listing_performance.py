"""
# Period Selection
Yesterday / MTD / M-1 / WTD / W-1 / Cumulative

# Calculation
1. new SKUs / live SKUs by gp acc. owner (done)
2. new SKUs / live SKUs by gp acc. owner + bd_index (done)
3. cumulative SKUs by lead source (done)
4. cumulative SKUs by gp acc. owner in different period (done)
5. yesterday / cumulative / w-1 / wtd / m-1 / mtd new SKUs / live SKUs by shop (done)

# query_id
994 for monthly performance
990 for weekly performance
1004 for yesterday performance

"""

import logging
import os
import time
import pandas as pd
from get_redash_query_result import get_fresh_query_result, get_shop_performance_by_certain_period
from get_particular_date import *
from get_google_sheets import upload_dataframe_to_google_sheet, upload_last_update_time

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# 输出的父目录
output_file_parent_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                          "Shopee 2016.4.12\\2017.2.21 Shop Level Summary"


def calculate_listing_performance():
    # 1.1 new_SKUs_by_gp_acc_owner dictionary
    new_SKUs_by_gp_acc_owner_list = {'Yesterday':
                                         [1004, 'Yesterday New SKUs by KAM'],
                                     'MTD':
                                         [994, 'MTD New SKUs by KAM'],
                                     'M-1':
                                         [994, 'M-1 New SKUs by KAM'],
                                     'WTD':
                                         [990, 'WTD New SKUs by KAM'],
                                     'W-1':
                                         [990, 'W-1 New SKUs by KAM'],
                                     'Cumulative':
                                         [1004, 'Cumulative SKUs by KAM']}

    def calculate_new_SKUs_by_gp_acc_owner(period):
        column_prefix = period.lower()
        # choose query_id
        query_id = new_SKUs_by_gp_acc_owner_list[period][0]

        performance_data = get_shop_performance_by_certain_period(query_id)

        performance_data_group = performance_data.groupby([performance_data['GP Account Owner'],
                                                           performance_data['country']])
        performance_data_result = performance_data_group.agg({column_prefix + '_skus': 'sum',
                                                              column_prefix + '_live_skus': 'sum'}).reset_index()

        # upload to google sheet
        google_sheet_id = '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
        google_sheet_name = new_SKUs_by_gp_acc_owner_list[period][1]

        logging.info('Start to upload ' + google_sheet_name + ' to google sheet.')
        upload_dataframe_to_google_sheet(performance_data_result,
                                         google_sheet_id,
                                         google_sheet_name)

        logging.info(google_sheet_name + ' is uploaded to google sheet.')

        return performance_data_result

    # 2.1 cumulative_SKUs_by_lead_source
    cumulative_SKUs_by_lead_source_list = {'Cumulative':
                                               [1004, 'Cumulative SKUs by Lead Source']}

    def calculate_cumulative_SKUs_by_lead_source(period):
        column_prefix = period.lower()
        # choose query_id
        query_id = cumulative_SKUs_by_lead_source_list[period][0]

        performance_data = get_shop_performance_by_certain_period(query_id)

        performance_data = performance_data[performance_data['Seller Launched by OB?'] == 1]

        performance_data_group = performance_data.groupby([performance_data['Source'],
                                                           performance_data['Key Brands 1']])
        performance_data_result = performance_data_group.agg({column_prefix + '_skus': 'sum',
                                                              column_prefix + '_live_skus': 'sum'}).reset_index()

        # upload to google sheet
        google_sheet_id = '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8'
        google_sheet_name = cumulative_SKUs_by_lead_source_list[period][1]

        logging.info('Start to upload ' + google_sheet_name + ' to google sheet.')
        upload_dataframe_to_google_sheet(performance_data_result,
                                         google_sheet_id,
                                         google_sheet_name)

        logging.info(google_sheet_name + ' is uploaded to google sheet.')

        return performance_data_result

    # 3.1 cumulative_SKUs_by_gp_acc_owner_in_different_period
    cumulative_SKUs_by_gp_acc_owner_in_different_period_list \
        = {'Cumulative':
               [1004, 'Cumulative SKUs by GP Acc in different period']}

    def calculate_cumulative_SKUs_by_gp_acc_owner_in_different_period(period):
        column_prefix = period.lower()
        # choose query_id
        query_id = cumulative_SKUs_by_gp_acc_owner_in_different_period_list[period][0]
        # three stage
        stage_list = ['GP Acc Created at M-1',
                      'GP Acc Created at M-2',
                      'GP Acc Created at M-3']

        performance_data = get_shop_performance_by_certain_period(query_id)

        performance_data_group = performance_data.groupby([performance_data['GP Account Owner'],
                                                           performance_data[stage_list[0]],
                                                           performance_data[stage_list[1]],
                                                           performance_data[stage_list[2]]
                                                           ])
        performance_data_result = performance_data_group.agg({column_prefix + '_skus': 'sum'}).reset_index()

        for index, stage in enumerate(stage_list):
            stage_result = performance_data_result[['GP Account Owner',
                                                    stage,
                                                    column_prefix + '_skus']] \
                .rename(columns={column_prefix + '_skus': stage + ' Cumulative SKUs'})
            stage_result = stage_result[stage_result[stage] == 1]
            stage_result = stage_result[['GP Account Owner', stage + ' Cumulative SKUs']]

            if index == 0:
                concat_result = stage_result
            else:
                concat_result = pd.merge(concat_result, stage_result, how='outer',
                                         left_on=['GP Account Owner'], right_on=['GP Account Owner'])

        concat_result = concat_result.fillna(0)

        # upload to google sheet
        google_sheet_id = '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8'
        google_sheet_name = cumulative_SKUs_by_gp_acc_owner_in_different_period_list[period][1]

        logging.info('Start to upload ' + google_sheet_name + ' to google sheet.')
        upload_dataframe_to_google_sheet(concat_result,
                                         google_sheet_id,
                                         google_sheet_name)

        logging.info(google_sheet_name + ' is uploaded to google sheet.')

        return concat_result

    # 4.1 SKUs_by_shop_in_different_period
    SKUs_by_shop_in_different_period_list = {'Yesterday':
                                                 [1004, 'Yesterday_SKUs_by_Shop'],
                                             'MTD':
                                                 [994, 'MTD_SKUs_by_Shop'],
                                             'M-1':
                                                 [994, 'M-1_SKUs_by_Shop'],
                                             'WTD':
                                                 [990, 'WTD_SKUs_by_Shop'],
                                             'W-1':
                                                 [990, 'W-1_SKUs_by_Shop'],
                                             'Cumulative':
                                                 [1004, 'Cumulative_SKUs_by_Shop']}

    def calculate_SKUs_by_shop_in_different_period_list(period):
        column_prefix = period.lower()
        # choose query_id
        query_id = SKUs_by_shop_in_different_period_list[period][0]

        performance_data = get_shop_performance_by_certain_period(query_id)

        performance_data_group = performance_data.groupby([performance_data['Child UserID'],
                                                           performance_data['Child ShopID']])
        performance_data_result = performance_data_group.agg({column_prefix + '_skus': 'sum',
                                                              column_prefix + '_live_skus': 'sum'}).reset_index()

        # export to folder
        file_name = SKUs_by_shop_in_different_period_list[period][1] + '.csv'
        file_path = os.path.join(output_file_parent_path, period, file_name)

        logging.info('Start to export ' + file_name + ' to folder.')
        performance_data_result.to_csv(file_path, sep=',')
        logging.info(file_name + ' is exported to folder.')

        return performance_data_result

    # 5.1 MTD_new_SKUs_by_gp_acc_owner_by_country
    def calculate_MTD_new_SKUs_by_gp_acc_owner_by_country():
        country_list = ['sg', 'my', 'tw', 'id', 'th', 'ph']
        start_date = get_start_of_this_month().strftime('%Y-%m-%d')
        end_date = get_yesterday_date().strftime('%Y-%m-%d')

        execute_success = None

        while execute_success is None:
            try:
                for index, country in enumerate(country_list):
                    params = {'p_country': country,
                              'p_start_date': start_date,
                              'p_end_date': end_date}

                    get_MTD_new_SKUs_by_gp_acc_owner_by_country \
                        = get_fresh_query_result('http://10.12.5.53',
                                                 1240,
                                                 'PrsLn6Mf09MuBxBTrAEeRdT3gyqKzbG20obScoEV',
                                                 params)

                    if index == 0:
                        final_result = get_MTD_new_SKUs_by_gp_acc_owner_by_country
                    else:
                        final_result = final_result.append(get_MTD_new_SKUs_by_gp_acc_owner_by_country)
                execute_success = 1
            except Exception as err:
                logging.info('An exception occurred: ' + str(err) + ', try again.')
                time.sleep(60)
                pass

        final_result = pd.pivot_table(final_result, values=['skus'],
                                      index=['GP Account Owner', 'country'], columns=['item_ctime'], aggfunc='sum')\
            .reset_index()

        final_result.columns = final_result.columns.droplevel(0)

        # 补充两列列名，不然上传会报错
        final_result.columns.values[0] = 'GP Account Owner'
        final_result.columns.values[1] = 'Country'

        final_result = final_result.fillna(0)

        # upload to google sheet
        google_sheet_id = '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
        google_sheet_name = 'MTD_Daily_New_SKUs_by_GP_Acc_Owner'

        logging.info('Start to upload ' + google_sheet_name + ' to google sheet.')
        upload_dataframe_to_google_sheet(final_result,
                                         google_sheet_id,
                                         google_sheet_name)

        logging.info(google_sheet_name + ' is uploaded to google sheet.')

        return final_result

    # 1.2 calculate_new_SKUs_by_gp_acc_owner
    for key, value in new_SKUs_by_gp_acc_owner_list.items():
        calculate_new_SKUs_by_gp_acc_owner(key)

    # 2.2 calculate_cumulative_SKUs_by_lead_source
    for key, value in cumulative_SKUs_by_lead_source_list.items():
        calculate_cumulative_SKUs_by_lead_source(key)

    # 3.2 calculate_cumulative_SKUs_by_gp_acc_owner_in_different_period
    for key, value in cumulative_SKUs_by_gp_acc_owner_in_different_period_list.items():
        calculate_cumulative_SKUs_by_gp_acc_owner_in_different_period(key)

    # 4.2 calculate_SKUs_by_shop_in_different_period
    for key, value in SKUs_by_shop_in_different_period_list.items():
        calculate_SKUs_by_shop_in_different_period_list(key)

    # 5.2 calculate_MTD_new_SKUs_by_gp_acc_owner_by_country
    calculate_MTD_new_SKUs_by_gp_acc_owner_by_country()

    # 更新GP Account Owner Performance Report (Daily)
    upload_last_update_time('1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM', 'Description', 'D5')
    # 更新BD Performance Report (Daily)
    upload_last_update_time('1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8', 'Description', 'D6')


if __name__ == '__main__':
    calculate_listing_performance()
