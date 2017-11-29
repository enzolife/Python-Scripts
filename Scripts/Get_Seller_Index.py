import pandas as pd
import numpy as np
from Scripts.Get_Google_Sheets import get_certain_google_sheets_to_dataframe
from Scripts.Get_Particular_Date import *
from Scripts.Get_File_Create_Modify_Time import *
from Scripts.Get_Lead_Index import get_lead_index_from_google_sheet


# 两种方法，一种是读本地csv，一种是读google sheet上的seller index
# 第二种方法中，先判断seller index今天有没有下载，然后取seller index到本地，再读取本地文件


# 方法1
def get_seller_index_from_local_xlsx():
    file_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12" \
                "\\2016.8.28 Seller Index Data\\Get_Seller_Index_from_Salesforce.xlsm"
    seller_index = pd.read_excel(file_path, sheetname='Seller Index')
    return seller_index


# 方法2
def get_seller_index_from_google_sheet():

    # 先判断今天的seller index是否下载
    # 如果未下载，则下载一份最新的到本地
    seller_index_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12" \
                        "\\2016.8.28 Seller Index Data\\seller_index.csv"
    seller_index_last_update_date = last_modify_date(seller_index_path)
    if seller_index_last_update_date != get_today_date().strftime("%Y-%m-%d"):
        book_name = 'Seller_Index_from_Salesforce'
        select_sheet = 'Raw_Seller_Index'
        seller_index = get_certain_google_sheets_to_dataframe(book_name, select_sheet)
        seller_index.to_csv(seller_index_path, sep=',')

    pwd = os.getcwd()
    os.chdir(os.path.dirname(seller_index_path))
    seller_index = pd.read_csv(os.path.basename(seller_index_path), index_col=None, header=0, encoding="GB18030")
    os.chdir(pwd)

    # Merge BD Index
    bd_index = get_lead_index_from_google_sheet()
    seller_index = pd.merge(seller_index, bd_index, how='left',
                            left_on=['GP Account Lead Name'],
                            right_on=['Sales Lead: Lead Name'])

    # 修改日期格式
    seller_index['GP Account Shopee Account Created Date'] \
        = pd.to_datetime(seller_index['GP Account Shopee Account Created Date'], format='%d/%m/%Y')
    seller_index['Yesterday Date'] = get_yesterday_date()
    seller_index['Yesterday Date'] = pd.to_datetime(seller_index['Yesterday Date'])
    seller_index['Date Transferred to Onboarding Queue']\
        = pd.to_datetime(seller_index['Date Transferred to Onboarding Queue'])

    # 添加GP Acc Created on M-1/M-2/M-3
    # 如果是M-1，参考Date Transferred to Onboarding Queue
    i = 1
    while i <= 3:
        seller_index['GP Acc Created at M-' + str(i)] = np.where(
            (seller_index['GP Account Shopee Account Created Date']
             <= get_start_end_of_certain_month(i, 'end')) & (
                seller_index['GP Account Shopee Account Created Date']
                >= get_start_end_of_certain_month(i, 'start')), 1, 0)
        i = i + 1
    return seller_index


# 获得去重的GP Acc列表
def get_gp_acc_index():
    seller_index = get_seller_index_from_google_sheet()
    gp_pre_index = seller_index[['GP Account ID',
                                 'GP Account Name',
                                 'GP Account Owner',
                                 'GP Account Shopee Account Created Date']]
    gp_pre_index = gp_pre_index.drop_duplicates()
    # 昨天，修改于GP Acc Shopee Acc Created Date同样的type
    gp_pre_index['Yesterday Date'] = get_yesterday_date()
    gp_pre_index['Yesterday Date'] = pd.to_datetime(gp_pre_index['Yesterday Date'])

    # 添加GP Acc Created on M-1/M-2/M-3
    i = 1
    while i <= 3:
        gp_pre_index['GP Acc Created at M-' + str(i)] = np.where(
            (gp_pre_index['GP Account Shopee Account Created Date']
             <= get_start_end_of_certain_month(i, 'end')) & (
                gp_pre_index['GP Account Shopee Account Created Date']
                >= get_start_end_of_certain_month(i, 'start')), 1, 0)
        i = i + 1
    return gp_pre_index


if __name__ == '__main__':
    # frame = get_gp_acc_index()
    frame = get_seller_index_from_google_sheet()
    # print(frame)
    # frame.to_csv('D://gp_acc_index.csv', sep=',')
    frame.to_csv('D://seller_index.csv', sep=',', encoding="GB18030")
