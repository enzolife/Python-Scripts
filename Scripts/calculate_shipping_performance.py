import logging
import os
import time
import pandas as pd
import numpy as np
from Scripts.get_redash_query_result import get_shop_performance_by_certain_period, get_fresh_query_result
from Scripts.Get_Particular_Date import *
from Scripts.Get_Google_Sheets \
    import upload_dataframe_to_google_sheet, upload_last_update_time, get_certain_google_sheets_to_dataframe_by_key
from Scripts.Get_Seller_Index import get_seller_index_from_google_sheet

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# seller_index
seller_index = get_seller_index_from_google_sheet()


def calculate_shipping_performance():
    def calculate_shipping_status_by_shop():
        country_list = ['sg', 'my', 'tw', 'id', 'th', 'ph']
        order_status_by_shop_with_all_country = pd.DataFrame()

        for index, country in enumerate(country_list):
            order_status_by_shop_sheet_name = country + 'cny_shop'

            order_status_by_shop_sheet \
                = get_certain_google_sheets_to_dataframe_by_key('1LZso15dMEjTFzVlapCfQFyf8QsC6dl447K0_2Xb9Wu4',
                                                                order_status_by_shop_sheet_name)

            order_status_by_shop_final_sheet = pd.merge(order_status_by_shop_sheet, seller_index,
                                                        left_on=['shopid'], right_on=['Child ShopID'], how='left')

            selected_columns = ['shopid', 'Child Account Name', 'GP Account Name', 'GP Account Owner',
                                'total_gross_order', 'cancel_order', 'NO_TN', 'info_receive_only',
                                'info_receive_only_DTS0', 'info_receive_only_DTS07',
                                'info_receive_only_DTS7', 'WH_inbound', 'in_transit', 'delivered']

            order_status_by_shop_final_sheet = order_status_by_shop_final_sheet[selected_columns]

            # 排序
            order_status_by_shop_final_sheet = \
                order_status_by_shop_final_sheet.sort_values(by=['info_receive_only'], ascending=False)

            # 上传
            upload_dataframe_to_google_sheet(order_status_by_shop_final_sheet,
                                             '1LZso15dMEjTFzVlapCfQFyf8QsC6dl447K0_2Xb9Wu4',
                                             order_status_by_shop_sheet_name + '_with_gp_info')

            # 合并所有国家
            order_status_by_shop_with_all_country = \
                order_status_by_shop_with_all_country.append(order_status_by_shop_final_sheet)

        # 排序
        order_status_by_shop_with_all_country =\
            order_status_by_shop_with_all_country.sort_values(by=['info_receive_only'], ascending=False).reset_index()

        order_status_by_shop_with_all_country.to_csv('D:\\test.csv', sep=',')

        upload_dataframe_to_google_sheet(order_status_by_shop_with_all_country.head(1000),
                                         '1LZso15dMEjTFzVlapCfQFyf8QsC6dl447K0_2Xb9Wu4',
                                         'all_country_cny_shop_with_gp_info')

    calculate_shipping_status_by_shop()


if __name__ == '__main__':
    calculate_shipping_performance()