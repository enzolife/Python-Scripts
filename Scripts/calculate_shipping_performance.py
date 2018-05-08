import logging
import os
import time
import pandas as pd
import numpy as np
from get_redash_query_result import get_shop_performance_by_certain_period, get_fresh_query_result
from Get_Particular_Date import *
from Get_Google_Sheets \
    import upload_dataframe_to_google_sheet, upload_last_update_time, get_certain_google_sheets_to_dataframe_by_key, \
    get_certain_google_sheets_to_dataframe
from Get_Seller_Index import get_seller_index_from_google_sheet
from get_redash_query_result import get_fresh_query_result_and_upload_to_google_sheet

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
        order_status_by_shop_with_all_country = \
            order_status_by_shop_with_all_country.sort_values(by=['info_receive_only'], ascending=False).reset_index()

        order_status_by_shop_with_all_country.to_csv('D:\\test.csv', sep=',')

        upload_dataframe_to_google_sheet(order_status_by_shop_with_all_country.head(1000),
                                         '1LZso15dMEjTFzVlapCfQFyf8QsC6dl447K0_2Xb9Wu4',
                                         'all_country_cny_shop_with_gp_info')

    def calculate_dts_pt_by_shop_by_gp_acc():
        dts_pt_by_shop = get_certain_google_sheets_to_dataframe('卖家备货时间模板', 'TWDTSPT_L14')
        dts_pt_by_shop_by_by_gp_acc = pd.merge(dts_pt_by_shop, seller_index,
                                               how='left', left_on='shopid', right_on='Child ShopID')

        selected_columns = ['shopid', 'Child Account Name', 'GP Account Name', 'GP Account Owner',
                            'Child Account Record Type', 'Child Account Owner',
                            '# Total WH receive order', '# Total WH receive order DTS>=7', '% of DTS>=7 order',
                            '# Total WH receive order PT>=7', '% of PT>=7 order', 'Average DTS',
                            '90 percentile DTS', 'Average PT', '90 percentile PT']

        dts_pt_by_shop_by_by_gp_acc = dts_pt_by_shop_by_by_gp_acc[selected_columns]

        upload_dataframe_to_google_sheet(dts_pt_by_shop_by_by_gp_acc,
                                         '12ifonVLZXICW_xTp8VTma7v6mXK5UDnX_LI7cxkzikc',
                                         'tw_dts_pt')

    def calculate_dts_penetration_by_shop():
        get_fresh_query_result_and_upload_to_google_sheet(2006,
                                                          {},
                                                          '1pW0x8rWRTRg3fUO6hcYEgJHJQI9sG4SESZ02H4uwUZc',
                                                          'preferred_mall_shop_pre_order_skus_tw')

    # calculate_shipping_status_by_shop()

    calculate_dts_pt_by_shop_by_gp_acc()

    # calculate_dts_penetration_by_shop()


if __name__ == '__main__':
    calculate_shipping_performance()
