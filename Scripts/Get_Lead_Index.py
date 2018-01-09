import pandas as pd
import numpy as np
from Scripts.Get_Google_Sheets import get_certain_google_sheets_to_dataframe
from Scripts.Get_Particular_Date import *
from Scripts.Get_File_Create_Modify_Time import *


# 两种方法，一种是读本地csv，一种是读google sheet上的lead index
# 第二种方法中，先判断lead index今天有没有下载，然后取seller index到本地，再读取本地文件


# 方法1
def get_lead_index_from_local_xlsx():
    file_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12" \
                "\\2017.8.11 Lead Index Data\\Get_Lead_Index.xlsm"
    lead_index = pd.read_excel(file_path, sheetname='Lead Index')
    return lead_index


# 方法2
def get_lead_index_from_google_sheet():
    # 先判断今天的lead index是否下载
    # 如果未下载，则下载一份最新的到本地
    lead_index_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12" \
                      "\\2017.8.11 Lead Index Data\\lead_index.csv"
    lead_index_last_update_date = last_modify_date(lead_index_path)
    if lead_index_last_update_date != get_today_date().strftime("%Y-%m-%d"):
        book_name = 'All leads'
        select_sheet = 'raw_leads'
        lead_index = get_certain_google_sheets_to_dataframe(book_name, select_sheet)
        lead_index.to_csv(lead_index_path, sep=',')

    pwd = os.getcwd()
    os.chdir(os.path.dirname(lead_index_path))
    lead_index = pd.read_csv(os.path.basename(lead_index_path), header=0, encoding="GB18030")
    os.chdir(pwd)

    # 转换日期格式
    lead_index['Sales Lead: Created Date'] = pd.to_datetime(lead_index['Sales Lead: Created Date'], format='%d/%m/%Y')
    lead_index['Claimed Date'] = pd.to_datetime(lead_index['Claimed Date'], format='%d/%m/%Y')
    lead_index['Date of Status Changed From Open'] = pd.to_datetime(lead_index['Date of Status Changed From Open'],
                                                                    format='%d/%m/%Y')
    # lead_index['Sales Lead: Lead Name'] = lead_index['Sales Lead: Lead Name'].str.encode('iso-8859-1')

    # 补充空值
    lead_index['Source'] = lead_index['Source'].fillna("N/A")
    lead_index['Key Brands 1'] = lead_index['Key Brands 1'].fillna("N/A")
    lead_index['Lead Source Details'] = lead_index['Lead Source Details'].fillna("N/A")

    # 修改格式
    lead_index['Open Lead Duration'] = lead_index['Open Lead Duration'].apply(pd.to_numeric).fillna(0)
    lead_index['Average Sales Cycle'] = lead_index['Average Sales Cycle'].apply(pd.to_numeric).fillna(0)

    # 增加判断列
    lead_index['CB Lead?'] = np.where(lead_index['Seller Classification'] == 'CB Trader', 1, 0)
    lead_index['Taobao Lead?'] = np.where(lead_index['Seller Classification'] == 'Taobao Seller', 1, 0)
    lead_index['Leads contacted?'] = np.where(lead_index['Lead Status'] == 'Open', 0, 1)
    lead_index['Leads Already Live?'] = np.where(lead_index['Lead Status'] == 'Already Live', 1, 0)
    lead_index['Leads Passed to OB?'] = np.where(lead_index['Sales Lead: Owner Name'] == 'Mei Wenjuan', 1,
                                                 np.where(lead_index['Sales Lead: Owner Name'] == 'Leon Chen', 1, 0))
    lead_index['Seller Launched by OB?'] = np.where(lead_index['Leads Already Live?']
                                                    + lead_index['Leads Passed to OB?'] == 2, 1, 0)

    return lead_index


def get_on_board_lead():
    # 先判断今天的on board lead index是否下载
    # 如果未下载，则下载一份最新的到本地
    on_board_lead_index_path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12" \
                               "\\2017.8.11 Lead Index Data\\on_board_lead_index.csv"
    on_board_lead_index_last_update_date = last_modify_date(on_board_lead_index_path)
    if on_board_lead_index_last_update_date != get_today_date().strftime("%Y-%m-%d"):
        book_name = 'on_board'
        select_sheet = 'raw_on_board'
        on_board_lead_index = get_certain_google_sheets_to_dataframe(book_name, select_sheet)
        on_board_lead_index.to_csv(on_board_lead_index_path, sep=',')

    pwd = os.getcwd()
    os.chdir(os.path.dirname(on_board_lead_index_path))
    on_board_lead_index = pd.read_csv(os.path.basename(on_board_lead_index_path),
                                      index_col=None, header=0, encoding="GB18030")
    os.chdir(pwd)

    return on_board_lead_index


if __name__ == '__main__':
    frame = get_lead_index_from_google_sheet()
    print(frame.info())
    frame.to_csv("D://lead_index.csv", sep=',')
