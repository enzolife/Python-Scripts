import pandas as pd
import numpy as np
from Get_Google_Sheets \
    import get_certain_google_sheets_to_dataframe, get_certain_google_sheets_to_dataframe_by_key
from Get_Particular_Date import *
from Get_File_Create_Modify_Time import *
from Get_Lead_Index import get_lead_index_from_google_sheet


# 两种方法，一种是读本地csv，一种是读google sheet上的seller index
# 第二种方法中，先判断seller index今天有没有下载，然后取seller index到本地，再读取本地文件

# 方法1
def get_seller_index_from_local_xlsx():
    file_path = "\\\\10.12.50.3\\data_source\\Seller_index\\Seller Index from Salesforce.xlsx"
    seller_index = pd.read_excel(file_path, sheetname='Sheet1')
    return seller_index


# 方法2
def get_seller_index_from_google_sheet():

    seller_index_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12" \
                        "\\2016.8.28 Seller Index Data\\seller_index.csv"

    """
    # 先判断今天的seller index是否下载
    # 如果未下载，则下载一份最新的到本地
    seller_index_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12" \
                        "\\2016.8.28 Seller Index Data\\seller_index.csv"
    seller_index_last_update_date = last_modify_date(seller_index_path)
    if seller_index_last_update_date != get_today_date().strftime("%Y-%m-%d"):
        book_name = 'Seller_Index_from_Salesforce'
        select_sheet = 'Raw_Seller_Index'
        seller_index = get_certain_google_sheets_to_dataframe(book_name, select_sheet)
        # 去除无用的行
        seller_index = seller_index[(seller_index['Child Account Record Type'] != np.NAN)]
        seller_index.to_csv(seller_index_path, sep=',')
    """
    seller_index = get_seller_index_from_local_xlsx()
    seller_index = seller_index[:-5]
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
    seller_index['GP Date Transferred From Onboarding Team']\
        = pd.to_datetime(seller_index['GP Date Transferred From Onboarding Team'], format='%d/%m/%Y')
    seller_index['Date Transferred From Onboarding Team'] \
        = pd.to_datetime(seller_index['Date Transferred From Onboarding Team'], format='%d/%m/%Y')

    # 添加country
    seller_index['Child Account Record Type - Country']\
        = seller_index['Child Account Record Type'].str.split('-').str[1]

    # 添加GP Acc Created on M-1/M-2/M-3
    # 如果是M-1，参考GP Date Transferred From Onboarding Team
    i = 1
    while i <= 3:
        seller_index['GP Acc Created at M-' + str(i)] = np.where(
            (seller_index['GP Date Transferred From Onboarding Team']
             <= get_start_end_of_certain_month(i, 'end')) & (
                seller_index['GP Date Transferred From Onboarding Team']
                >= get_start_end_of_certain_month(i, 'start')), 1, 0)
        i = i + 1

    return seller_index


# 获得去重的GP Acc列表
def get_gp_acc_index():
    seller_index = get_seller_index_from_google_sheet()
    gp_pre_index = seller_index[['GP Account ID',
                                 'GP Account Name',
                                 'GP Account Owner',
                                 'GP Date Transferred From Onboarding Team',
                                 'GP Account Shopee Account Created Date']]
    gp_pre_index = gp_pre_index.drop_duplicates()
    # 昨天，修改于GP Acc Shopee Acc Created Date同样的type
    gp_pre_index['Yesterday Date'] = get_yesterday_date()
    gp_pre_index['Yesterday Date'] = pd.to_datetime(gp_pre_index['Yesterday Date'])

    # 添加GP Acc Created on M-1/M-2/M-3
    i = 1
    while i <= 3:
        gp_pre_index['GP Acc Created at M-' + str(i)] = np.where(
            (gp_pre_index['GP Date Transferred From Onboarding Team']
             <= get_start_end_of_certain_month(i, 'end')) & (
                gp_pre_index['GP Date Transferred From Onboarding Team']
                >= get_start_end_of_certain_month(i, 'start')), 1, 0)
        i = i + 1
    return gp_pre_index


# 获得new shop index
def get_new_shop_index():

    new_shop_index_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12" \
                          "\\2016.8.28 Seller Index Data\\new_shop_index.csv"

    new_shop_index_last_update_date = last_modify_date(new_shop_index_path)

    # if new_shop_index_last_update_date != get_today_date().strftime("%Y-%m-%d"):
    book_key = "1bJ4Un9Q7yJkt2QfKJGt2Pk21VnjBRmLgGwn5ewaWdf4"

    old_list = get_certain_google_sheets_to_dataframe_by_key(book_key, 'New_shop_before_2018/1/30')
    new_list = get_certain_google_sheets_to_dataframe_by_key(book_key, 'Total')

    old_list = old_list[['Child ShopID', 'new_shop_date']]
    new_list = new_list[['Child ShopID', 'date']].rename(columns={'date': 'new_shop_date'})

    new_shop_index = pd.concat([old_list, new_list])

    # new_shop_index = pd.concat(list_)
    new_shop_index.to_csv(new_shop_index_path, sep=',')

    pwd = os.getcwd()
    os.chdir(os.path.dirname(new_shop_index_path))
    new_shop_index = pd.read_csv(os.path.basename(new_shop_index_path), index_col=None, header=0, encoding="GB18030")
    os.chdir(pwd)

    # Merge Seller Index
    seller_index = get_seller_index_from_google_sheet()
    new_shop_index = pd.merge(new_shop_index, seller_index, how='left',
                              left_on=['Child ShopID'], right_on=['Child ShopID'])

    new_shop_index['country'] = new_shop_index['Child Account Record Type'].str.split('-').str[1]
    new_shop_index['new_shop_date'] = pd.to_datetime(new_shop_index['new_shop_date'])
    new_shop_index = new_shop_index.drop_duplicates(['Child ShopID'], keep='first')

    new_shop_index = new_shop_index[['new_shop_date',
                                     'country',
                                     'Child ShopID',
                                     'Child Account Name',
                                     'Child Account Owner',
                                     'Child Account Record Type',
                                     'GP Account ID',
                                     'GP Account Lead Name',
                                     'GP Account Lead Size',
                                     'GP Account Name',
                                     'GP Account Owner',
                                     'GP Account Seller Classification',
                                     'GP Account Shopee Account Created Date',
                                     'Shopee Account Created Date'
                                     ]]

    return new_shop_index


# 获得new shop index
def get_new_shop_index_abandon():

    new_shop_index_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12" \
                          "\\2016.8.28 Seller Index Data\\new_shop_index.csv"

    new_shop_index_last_update_date = last_modify_date(new_shop_index_path)

    if new_shop_index_last_update_date != get_today_date().strftime("%Y-%m-%d"):
        book_name = "New Shop Tracker"
        selected_sheet = ['SG', 'MY', 'TW', 'ID', 'TH', 'PH']
        list_ = []
        for country_sheet in selected_sheet:
            country_new_shop_index = get_certain_google_sheets_to_dataframe(book_name, country_sheet)
            list_.append(country_new_shop_index)

        new_shop_index = pd.concat(list_)
        new_shop_index.to_csv(new_shop_index_path, sep=',')

    pwd = os.getcwd()
    os.chdir(os.path.dirname(new_shop_index_path))
    new_shop_index = pd.read_csv(os.path.basename(new_shop_index_path), index_col=None, header=0, encoding="GB18030")
    os.chdir(pwd)

    # 修改日期格式
    new_shop_index['Update date'] = pd.to_datetime(new_shop_index['Update date'])

    # 有些商店重复达到50个LIVE SKUS的门槛，我们只取最开始的那个创建时间
    new_shop_index = new_shop_index.sort(['Shop id', 'Update date'], ascending=[1, 1])
    new_shop_index = new_shop_index.drop_duplicates(['Shop id'], keep='first')

    # Merge Seller Index
    seller_index = get_seller_index_from_google_sheet()
    new_shop_index = pd.merge(new_shop_index, seller_index, how='left', left_on=['Shop id'], right_on=['Child ShopID'])

    new_shop_index = new_shop_index[['Shop id',
                                     'Update date',
                                     'Child Account Name',
                                     'Child Account Owner',
                                     'Child Account Record Type',
                                     'GP Account ID',
                                     'GP Account Lead Name',
                                     'GP Account Lead Size',
                                     'GP Account Name',
                                     'GP Account Owner',
                                     'GP Account Seller Classification',
                                     'GP Account Shopee Account Created Date',
                                     'Shopee Account Created Date',
                                     'Site',
                                     'Shop name',
                                     'Shop url',
                                     'PIC']]

    return new_shop_index


if __name__ == '__main__':
    # frame = get_gp_acc_index()
    frame = get_seller_index_from_google_sheet()
    # print(frame['Child Account Record Type - Country'].head())
    # frame = frame[frame['GP Account Owner ID'].isnull()]
    # print(frame)
    # frame.to_csv('D://gp_acc_index.csv', sep=',')
    frame.to_csv('D://seller_index.csv', sep=',', encoding="GB18030")

    # print(get_new_shop_index().head(100))
    # get_new_shop_index().to_csv('D://new_shop_index.csv', sep=',', encoding="GB18030")

