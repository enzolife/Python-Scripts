from pandas import Series, DataFrame
import pandas as pd
import glob
import os
import datetime
import time
from Scripts.Get_File_Create_Modify_Time import last_modify_date
from Scripts.Get_Particular_Date import *
from Scripts.Copy_Files_from_Intranet import *

from_path = "\\\\10.12.50.3\\data_source\\order_csv"


def get_concatenated_order_report():
    # 如果数据还没有从intranet下载下来，就返回false
    if check_data_validation(from_path) is False:
        return False
    else:
        copy_order_report_from_intranet()
        country_list = []
        path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
               'Shopee 2016.4.12\\2016.4.23 Data Visualization\\Order'
        allFiles = glob.glob(path + "\\*\\*.csv")
        frame = pd.DataFrame()
        list_ = []
        for file_ in allFiles:
            # pwd = os.getcwd()  # 首先取初始工作目录
            os.chdir(os.path.dirname(file_))  # 然后取SG/MY/TW/ID/TH这个文件夹
            country_name = os.path.basename(file_).split('_')[2][:2].upper()
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
        if country_list == ['ID', 'MY', 'SG', 'TH', 'TW']:
            for file_ in allFiles:
                pwd = os.getcwd()  # 首先取初始工作目录
                os.chdir(os.path.dirname(file_))  # 然后取SG/MY/TW/ID/TH这个文件夹

                df = pd.read_csv(os.path.basename(file_), index_col=None, header=0)  # 读取这份文件，不用带上前面那一堆路径
                list_.append(df)

                os.chdir(pwd)

            # 确认日期没错
            print('Today is: ' + today_date + ', Now concatenating order report.')

            frame = pd.concat(list_)

            return frame
        else:
            return False

if __name__ == '__main__':
    get_concatenated_order_report()

