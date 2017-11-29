from Scripts.Get_Lead_Index import get_lead_index_from_local_xlsx, get_lead_index_from_google_sheet
from Scripts.Get_Google_Sheets import upload_dataframe_to_google_sheet, upload_last_update_time
from Scripts.Get_Particular_Date import *
from Scripts.Get_Gmail_Config import send_message
import pandas as pd
import numpy as np


def get_bd_index_config():
    output_file_path = 'D:\\'

    bd_index = get_lead_index_from_google_sheet()

    # 补充空值
    bd_index['Source'] = bd_index['Source'].fillna("N/A")
    bd_index['Key Brands 1'] = bd_index['Key Brands 1'].fillna("N/A")
    bd_index['Lead Source Details'] = bd_index['Lead Source Details'].fillna("N/A")

    # 修改格式
    bd_index['Open Lead Duration'] = bd_index['Open Lead Duration'].apply(pd.to_numeric).fillna(0)
    bd_index['Average Sales Cycle'] = bd_index['Average Sales Cycle'].apply(pd.to_numeric).fillna(0)

    # 增加判断列
    bd_index['CB Lead?'] = np.where(bd_index['Seller Classification'] == 'CB Trader', 1, 0)
    bd_index['Taobao Lead?'] = np.where(bd_index['Seller Classification'] == 'Taobao Seller', 1, 0)
    bd_index['Leads contacted?'] = np.where(bd_index['Lead Status'] == 'Open', 0, 1)
    bd_index['Leads Already Live?'] = np.where(bd_index['Lead Status'] == 'Already Live', 1, 0)
    bd_index['Leads Passed to OB?'] = np.where(bd_index['Sales Lead: Owner Name'] == 'Mei Wenjuan', 1,
                                               np.where(bd_index['Sales Lead: Owner Name'] == 'Leon Chen', 1, 0))
    bd_index['Seller Launched by OB?'] = np.where(bd_index['Leads Already Live?'] + bd_index['Leads Passed to OB?'] == 2
                                                  , 1, 0)
    return bd_index


# 明细表
def get_initial_bd_performance_detail():
    bd_index = get_bd_index_config()
    return bd_index


# 初步计算结果
def get_initial_bd_performance_result():
    bd_index = get_bd_index_config()
    # 开始计算
    bd_index_group = bd_index.groupby([bd_index['Source'], bd_index['Lead Source Details']])
    bd_index_result = bd_index_group.agg({'Sales Lead: ID': 'count',
                                          'CB Lead?': 'sum',
                                          'Taobao Lead?': 'sum',
                                          'Leads contacted?': 'sum',
                                          'Leads Already Live?': 'sum',
                                          'Leads Passed to OB?': 'sum',
                                          'Seller Launched by OB?': 'sum',
                                          'Open Lead Duration': 'mean',
                                          'Average Sales Cycle': 'mean'}) \
        .rename(columns={'Sales Lead: ID': '# of Leads',
                         'CB Lead?': '# of CB Leads',
                         'Taobao Lead?': '# of Taobao Leads',
                         'Leads contacted?': '# of Leads contacted',
                         'Leads Already Live?': '# of Sellers from these Leads',
                         'Leads Passed to OB?': '# of Leads passed to OB Team',
                         'Seller Launched by OB?': '# of Sellers launched by OB Team'})

    # 增加百分比列
    bd_index_result['% CB Leads'] = bd_index_result['# of CB Leads'] / bd_index_result['# of Leads']
    bd_index_result['% Taobao Leads'] = bd_index_result['# of Taobao Leads'] / bd_index_result['# of Leads']
    bd_index_result['% Leads contacted'] = bd_index_result['# of Leads contacted'] / bd_index_result['# of Leads']
    bd_index_result['% of Lead Conversion'] = bd_index_result['# of Sellers from these Leads'] \
                                              / bd_index_result['# of Leads']
    bd_index_result['OB Team launch%'] = (bd_index_result['# of Sellers launched by OB Team']
                                          / bd_index_result['# of Leads passed to OB Team']).fillna(0)

    # 添加数据刷新时间
    bd_index_result['Last Update Date'] = get_yesterday_date()

    # 列顺序改变
    bd_index_result = bd_index_result[['# of Leads',
                                       '% CB Leads',
                                       '% Taobao Leads',
                                       '# of Leads contacted',
                                       '% Leads contacted',
                                       '# of Sellers from these Leads',
                                       '% of Lead Conversion',
                                       '# of Leads passed to OB Team',
                                       '# of Sellers launched by OB Team',
                                       'OB Team launch%',
                                       'Open Lead Duration',
                                       'Average Sales Cycle',
                                       'Last Update Date']]

    bd_index_result = pd.DataFrame(bd_index_result).reset_index()

    return bd_index_result


# 上传初步计算结果
def upload_bd_performance():
    initial_bd_performance_result_be_uploaded = get_initial_bd_performance_result()
    # 上传initial bd performance result
    upload_dataframe_to_google_sheet(initial_bd_performance_result_be_uploaded,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'Initial BD Performance Data')

    # 更新last update time
    upload_last_update_time('1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8', 'Description', 'D4')

    # 所有步骤执行完后，发一封邮件
    print('\nProcess completed!')
    send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date())
                 + ' BD Index Calculation Completed!', 'BD Index Calculation Completed!')


# 其它计算结果
# 两个月的Daily # of Leads
def calculate_num_of_leads_by_date():
    bd_index = get_bd_index_config()
    # 开始计算
    bd_index = bd_index[(bd_index['Sales Lead: Created Date'] >= get_start_of_last_month())
                        & (bd_index['Sales Lead: Created Date'] <= get_yesterday_date())]
    bd_index_group = bd_index.groupby([bd_index['Sales Lead: Created Date']])
    bd_index_result = bd_index_group.agg({'Sales Lead: ID': 'count',
                                          'CB Lead?': 'sum',
                                          'Taobao Lead?': 'sum',
                                          'Leads contacted?': 'sum',
                                          'Leads Already Live?': 'sum'}) \
        .rename(columns={'Sales Lead: ID': '# of Leads',
                         'CB Lead?': '# of CB Leads',
                         'Taobao Lead?': '# of Taobao Leads',
                         'Leads contacted?': '# of Leads contacted',
                         'Leads Already Live?': '# of Sellers from these Leads'})

    # 增加百分比列
    bd_index_result['% CB Leads'] = bd_index_result['# of CB Leads'] / bd_index_result['# of Leads']
    bd_index_result['% Taobao Leads'] = bd_index_result['# of Taobao Leads'] / bd_index_result['# of Leads']
    bd_index_result['% Leads contacted'] = bd_index_result['# of Leads contacted'] / bd_index_result['# of Leads']
    bd_index_result['% of Lead Conversion'] = bd_index_result['# of Sellers from these Leads'] \
                                              / bd_index_result['# of Leads']

    # 列顺序改变
    bd_index_result = bd_index_result[['# of Leads',
                                       '% CB Leads',
                                       '% Taobao Leads',
                                       '# of Leads contacted',
                                       '% Leads contacted',
                                       '# of Sellers from these Leads',
                                       '% of Lead Conversion']]

    # 上传calculate_num_of_leads_by_date
    upload_dataframe_to_google_sheet(bd_index_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'Initial Daily # of Leads')


# Leads in different stage
def calculate_num_of_leads_in_different_stage():
    bd_index = get_bd_index_config()
    # 开始计算
    bd_index = bd_index[(bd_index['Sales Lead: Created Date'] >= get_start_of_last_month())
                        & (bd_index['Sales Lead: Created Date'] <= get_yesterday_date())]
    bd_index_group = bd_index.groupby([bd_index['Sales Lead: Created Date']])
    bd_index_result = bd_index_group.agg({'Sales Lead: ID': 'count',
                                          'CB Lead?': 'sum',
                                          'Taobao Lead?': 'sum',
                                          'Leads contacted?': 'sum',
                                          'Leads Already Live?': 'sum'}) \
        .rename(columns={'Sales Lead: ID': '# of Leads',
                         'CB Lead?': '# of CB Leads',
                         'Taobao Lead?': '# of Taobao Leads',
                         'Leads contacted?': '# of Leads contacted',
                         'Leads Already Live?': '# of Sellers from these Leads'})

    # 增加百分比列
    bd_index_result['% CB Leads'] = bd_index_result['# of CB Leads'] / bd_index_result['# of Leads']
    bd_index_result['% Taobao Leads'] = bd_index_result['# of Taobao Leads'] / bd_index_result['# of Leads']
    bd_index_result['% Leads contacted'] = bd_index_result['# of Leads contacted'] / bd_index_result['# of Leads']
    bd_index_result['% of Lead Conversion'] = bd_index_result['# of Sellers from these Leads'] \
                                              / bd_index_result['# of Leads']

    # 列顺序改变
    bd_index_result = bd_index_result[['# of Leads',
                                       '% CB Leads',
                                       '% Taobao Leads',
                                       '# of Leads contacted',
                                       '% Leads contacted',
                                       '# of Sellers from these Leads',
                                       '% of Lead Conversion']]

    # 上传calculate_num_of_leads_by_date
    upload_dataframe_to_google_sheet(bd_index_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'Initial Daily # of Leads')

# Reject Reason
# def calculate_num_of_leads_by_rejected_reason():

if __name__ == '__main__':
    calculate_num_of_leads_by_date()
    upload_bd_performance()
