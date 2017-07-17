# coding: utf-8
import datetime
from pandas import Series, DataFrame
import pandas as pd
from Scripts.Get_Particular_Date import *
from Scripts.Get_Listing_Reports import get_concatenated_listing_report
from Scripts.Get_Gmail_Config import *


def calculate_sku_by_shop():
    # Listing Report的目录
    # input_file_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
                      # 'Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing'
    frame = get_concatenated_listing_report()

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
        print('Yesterday is: ' + yesterday.strftime("%Y-%m-%d") + ', Now calculating listing result.')

        # 转换Date Created的格式
        frame['Date Created'] = pd.to_datetime(frame['Date Created'])

        # 1.计算Yesterday
        print('\nCalculating Yesterday Data...')
        output_file_path = output_file_parent_path + "\\Yesterday\\"

        # 1.1 计算Yesterday New SKUs
        frame1 = frame[(frame['Date Created'] == yesterday)]
        grouped1 = frame1['Product ID'].groupby([frame1['Seller User ID'], frame1['Shop ID'], frame1['Username'], frame1['Country']])

        Yesterday_New_SKUs_by_Shop = grouped1.agg({'Product ID': {'New SKUs': 'count'}})
        Yesterday_New_SKUs_by_Shop.columns = Yesterday_New_SKUs_by_Shop.columns.droplevel(0)

        Yesterday_New_SKUs_by_Shop.to_csv(output_file_path + 'Yesterday_New_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('1.1 Yesterday_New_SKUs_by_Shop completed')

        # 1.2 计算Yesterday New Live SKUs
        frame2 = frame[(frame['Date Created'] == yesterday) & (frame['Status'] == 'Normal')]
        grouped2 = frame2['Product ID'].groupby([frame2['Seller User ID'], frame2['Shop ID'], frame2['Username'], frame2['Country']])

        Yesterday_New_Live_SKUs_by_Shop = grouped2.agg({'Product ID': {'New Live SKUs': 'count'}})
        Yesterday_New_Live_SKUs_by_Shop.columns = Yesterday_New_Live_SKUs_by_Shop.columns.droplevel(0)

        Yesterday_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'Yesterday_New_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('1.2 Yesterday_New_Live_SKUs_by_Shop completed')

        # 1.3 计算Cumulative SKUs
        grouped3 = frame['Product ID'].groupby([frame['Seller User ID'], frame['Shop ID'], frame['Username'], frame['Country']])

        Cumulative_SKUs_by_Shop = grouped3.agg({'Product ID': {'Cumulative SKUs': 'count'}})
        Cumulative_SKUs_by_Shop.columns = Cumulative_SKUs_by_Shop.columns.droplevel(0)

        Cumulative_SKUs_by_Shop.to_csv(output_file_path + 'Cumulative_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('1.3 Cumulative_SKUs_by_Shop completed')

        # 1.4 计算Cumulative Live SKUs
        frame4 = frame.loc[frame['Status'] == 'Normal']
        grouped4 = frame4['Product ID'].groupby([frame4['Seller User ID'], frame4['Shop ID'], frame4['Username'], frame4['Country']])

        Cumulative_Live_SKUs_by_Shop = grouped4.agg({'Product ID': {'Cumulative Live SKUs': 'count'}})
        Cumulative_Live_SKUs_by_Shop.columns = Cumulative_Live_SKUs_by_Shop.columns.droplevel(0)

        Cumulative_Live_SKUs_by_Shop.to_csv(output_file_path + 'Cumulative_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('1.4 Cumulative_Live_SKUs_by_Shop completed')

        # 2.计算WTD
        print('\nCalculating WTD Data...')
        output_file_path = output_file_parent_path + "\\WTD\\"

        # 2.1 计算WTD New SKUs
        frame5 = frame[(frame['Date Created'] >= start_of_this_week) & (frame['Date Created'] <= yesterday)]
        grouped5 = frame5['Product ID'].groupby([frame5['Seller User ID'], frame5['Shop ID'], frame5['Username'], frame5['Country']])

        WTD_New_SKUs_by_Shop = grouped5.agg({'Product ID': {'New SKUs': 'count'}})
        WTD_New_SKUs_by_Shop.columns = WTD_New_SKUs_by_Shop.columns.droplevel(0)

        WTD_New_SKUs_by_Shop.to_csv(output_file_path + 'WTD_New_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('2.1 WTD_New_SKUs_by_Shop completed')

        # 2.2 计算WTD New Live SKUs
        frame6 = frame[(frame['Date Created'] >= start_of_this_week) & (frame['Date Created'] <= yesterday) & (frame['Status'] == 'Normal')]
        grouped6 = frame6['Product ID'].groupby([frame6['Seller User ID'], frame6['Shop ID'], frame6['Username'], frame6['Country']])

        WTD_New_Live_SKUs_by_Shop = grouped6.agg({'Product ID': {'New Live SKUs': 'count'}})
        WTD_New_Live_SKUs_by_Shop.columns = WTD_New_Live_SKUs_by_Shop.columns.droplevel(0)

        WTD_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'WTD_New_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('2.2 WTD_New_Live_SKUs_by_Shop completed')

        # 3.计算W-1
        print('\nCalculating W-1 Data...')
        output_file_path = output_file_parent_path + "\\W-1\\"

        # 3.1 计算W-1 New SKUs
        frame7 = frame[(frame['Date Created'] >= start_of_last_week) & (frame['Date Created'] <= end_of_last_week)]
        grouped7 = frame7['Product ID'].groupby([frame7['Seller User ID'], frame7['Shop ID'], frame7['Username'], frame7['Country']])

        W_1_New_SKUs_by_Shop = grouped7.agg({'Product ID': {'New SKUs': 'count'}})
        W_1_New_SKUs_by_Shop.columns = W_1_New_SKUs_by_Shop.columns.droplevel(0)

        W_1_New_SKUs_by_Shop.to_csv(output_file_path + 'W_1_New_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('3.1 W_1_New_SKUs_by_Shop completed')

        # 3.2 计算W-1 New Live SKUs
        frame8 = frame[(frame['Date Created'] >= start_of_last_week) & (frame['Date Created'] <= end_of_last_week) & (frame['Status'] == 'Normal')]
        grouped8 = frame8['Product ID'].groupby([frame8['Seller User ID'], frame8['Shop ID'], frame8['Username'], frame8['Country']])

        W_1_New_Live_SKUs_by_Shop = grouped8.agg({'Product ID': {'New Live SKUs': 'count'}})
        W_1_New_Live_SKUs_by_Shop.columns = W_1_New_Live_SKUs_by_Shop.columns.droplevel(0)

        W_1_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'W_1_New_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('3.2 W_1_New_Live_SKUs_by_Shop completed')

        # 4.计算MTD
        print('\nCalculating MTD Data...')
        output_file_path = output_file_parent_path + "\\MTD\\"

        # 4.1 计算MTD New SKUs
        frame9 = frame[(frame['Date Created'] >= start_of_this_month) & (frame['Date Created'] <= yesterday)]
        grouped9 = frame9['Product ID'].groupby([frame9['Seller User ID'], frame9['Shop ID'], frame9['Username'], frame9['Country']])

        MTD_New_SKUs_by_Shop = grouped9.agg({'Product ID': {'New SKUs': 'count'}})
        MTD_New_SKUs_by_Shop.columns = MTD_New_SKUs_by_Shop.columns.droplevel(0)

        MTD_New_SKUs_by_Shop.to_csv(output_file_path + 'MTD_New_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('4.1 MTD_New_SKUs_by_Shop completed')

        # 4.2 计算MTD New Live SKUs
        frame10 = frame[(frame['Date Created'] >= start_of_this_month) & (frame['Date Created'] <= yesterday) & (frame['Status'] == 'Normal')]
        grouped10 = frame10['Product ID'].groupby([frame10['Seller User ID'], frame10['Shop ID'], frame10['Username'], frame10['Country']])

        MTD_New_Live_SKUs_by_Shop = grouped10.agg({'Product ID': {'New Live SKUs': 'count'}})
        MTD_New_Live_SKUs_by_Shop.columns = MTD_New_Live_SKUs_by_Shop.columns.droplevel(0)

        MTD_New_Live_SKUs_by_Shop.to_csv(output_file_path + 'MTD_New_Live_SKUs_by_Shop.csv', sep=',', encoding='utf-8')

        print('4.2 MTD_New_Live_SKUs_by_Shop completed')

        # 5.计算Cumulative
        # print('\nCalculating Cumulative Data...')
        # output_file_path = output_file_parent_path + "\\Cumulative\\"

        # 5.1 计算TW Banned Listing
        # banned_keyword_list = {'武士刀', '手仗刀', '鴛鴦刀', '匕首', '掃刀', '鏢刀', '鋼筆刀', '蛇刀', '警刀', '手槍', '衝鋒槍', '步槍',
                               # '散彈槍', '十字弓', '彈弓', '牙籤弩', '迷你弩', '槍弩', '箭', '刀', '炮', '弩', '手指虎', '甩棍', '警棍',
                               # '伸縮棍', '防衛棍', '鏢', '鋼鞭', '警銬', '警繩', '防爆網', '瓦斯', '催淚彈', '打火機', '電火機', '打火石',
                               # '火柴', '花生', '檳榔', '肉乾', '農產品', '充電寶', '行動電源', '海鮮', '瑞士刀', '軍刀', '菜刀',
                               # '水果刀', '戶外刀', '折刀', '彈簧刀', '火石', '打火石', '水彈槍'}

        #frame11 = frame[(frame['Country'] == 'TW') & (frame['Status'] == 'Normal')]
        #　banned_frame_list = []

        #　for banned_words in banned_keyword_list:
            # banned_frame_selected = frame11[(frame11['Product name'].str.contains(banned_words) == True)]
            # banned_frame_list.append(banned_frame_selected)

        # 注意：这里有可能产生重复值，需要去重
        # banned_frame_concat = pd.concat(banned_frame_list)
        # banned_frame_concat = banned_frame_concat.drop_duplicates(['Product ID'], keep='first')

        # banned_frame_concat.columns = banned_frame_concat.columns.droplevel(0)
        # banned_frame_concat.to_csv(output_file_path + 'Get_TW_Banned_Listing.csv', sep=',')

        # print('5.1 TW Banned Listing completed')

        # 所有步骤执行完后，发一封邮件
        print('\nProcess completed!')
        send_message('enzo.kuang@shopeemobile.com', '[Notices] ' + str(get_today_date())
                     + ' SKU Calculation Completed!', 'SKU Calculation Completed!')

if __name__ == '__main__':
    calculate_sku_by_shop()