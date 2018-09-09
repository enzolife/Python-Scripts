from pandas import Series, DataFrame
import pandas as pd
import glob
import os
import datetime
import time
from get_file_create_modify_time import last_modify_date
from get_particular_date import *
from copy_files_from_intranet import *

from_path = "\\\\10.12.50.3\\data_source\\listing_csv"


def get_concatenated_listing_report():
    # copy_listing_report_from_intranet()
    country_list = []
    path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
           'Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing'
    allFiles = glob.glob(path + "\\*\\*.csv")
    frame = pd.DataFrame()
    list_ = []
    for file_ in allFiles:
        # pwd = os.getcwd()  # 首先取初始工作目录
        os.chdir(os.path.dirname(file_))  # 然后取SG/MY/TW/ID/TH这个文件夹
        country_name = os.path.basename(file_).split('_')[0]
        file_create_time = last_modify_date(file_)
        today_date = get_today_date().strftime("%Y-%m-%d")

        # 如果creation_date不是今天，就跳出
        if file_create_time != today_date:
            break
        else:
            # 如果原来已经有了这个国家，就不用添加进去了
            if country_name not in country_list:
                country_list.append(country_name)
            country_list.sort()

    # 如果所有国家都齐备
    if country_list == ['ID', 'MY', 'PH', 'SG', 'TH', 'TW']:
        for file_ in allFiles:
            pwd = os.getcwd()  # 首先取初始工作目录
            os.chdir(os.path.dirname(file_))  # 然后取SG/MY/TW/ID/TH这个文件夹

            # print("Now concatenating " + str(os.getcwd()) + ".")

            # 只导入选择的列，避免乱码
            '''
            fields = ["Product ID", "Username", "Shopname", "Category", "Price", "Sold(complete)", "Stock",
                      "Images", "QC", "Status", "Live_status", "Likes", "Date Created", "Date Updated",
                      "Country", "Seller User ID", "Sold(total)", "Date generated", "Shop ID", "Sub category",
                      "Condition", "Price before discount"]
            '''

            fields = ["Product ID", "Username", "Shopname", "Category", "QC", "Status",
                      "Live_status", "Date Created", "Country", "Seller User ID", "Shop ID",
                      "Sub category", "Condition"]

            # 读取这份文件，不用带上前面那一堆路径
            df = pd.read_csv(os.path.basename(file_), index_col=None, header=0,
                             skipinitialspace=True, usecols=fields, chunksize=1000000)

            chunks = []
            for chunk in df:
                chunks.append(chunk)
            df2 = pd.concat(chunks, ignore_index=True)
            list_.append(df2)
            os.chdir(pwd)

        # 确认日期没错
        print('Today is: ' + today_date + ', Now concatenating listing report.')

        frame = pd.concat(list_)

        return frame
    else:
        return False

if __name__ == '__main__':
    # path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing"
    try:
        get_concatenated_listing_report()
    except Exception as err:
        print("An exception occur: " + str(err))


