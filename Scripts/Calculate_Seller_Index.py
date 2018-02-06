import pandas as pd
from Scripts.Get_Seller_Index import get_gp_acc_index, get_seller_index_from_google_sheet, get_new_shop_index
from Scripts.Get_Google_Sheets import *
from Scripts.Get_Gmail_Config import send_message


def calculate_num_of_seller_by_gp_acc_owner():
    gp_index = get_gp_acc_index()
    gp_index_group = gp_index.groupby([gp_index['GP Account Owner']])
    gp_index_result = gp_index_group.agg({'GP Account ID': 'count'})
    gp_index_result = pd.DataFrame(gp_index_result).reset_index()
    upload_dataframe_to_google_sheet(gp_index_result,
                                     '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM',
                                     '# of GP Acc by GP Acc Owner')


def calculate_num_of_seller_shops_by_gp_acc_owner_by_country():
    seller_index = get_seller_index_from_google_sheet()

    seller_index_group = seller_index.groupby(['GP Account Owner', 'Child Account Record Type'])
    seller_index_result = seller_index_group.agg({'GP Account Name': lambda x: x.nunique(),
                                                  'Child ShopID': 'count'})\
        .rename(columns={'GP Account Name': '# of Sellers',
                         'Child ShopID': '# of Shops'})\
        .reset_index()

    seller_index_result['Child Account Record Type']\
        = seller_index_result['Child Account Record Type'].str.split('-').str[1]

    # 上传
    upload_dataframe_to_google_sheet(seller_index_result,
                                     '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM',
                                     '# of GP Acc by GP Acc Owner by Country')


def calculate_num_of_seller_in_different_stage_by_gp_acc():
    gp_index = get_gp_acc_index()
    gp_index_group = gp_index.groupby([gp_index['GP Account Owner']])
    gp_index_result = gp_index_group.agg({'GP Acc Created at M-1': 'sum',
                                          'GP Acc Created at M-2': 'sum',
                                          'GP Acc Created at M-3': 'sum'})
    gp_index_result = pd.DataFrame(gp_index_result).reset_index()
    upload_dataframe_to_google_sheet(gp_index_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'Initial # of Sellers')


def calculate_num_of_shop_in_different_stage_by_gp_acc():
    seller_index = get_seller_index_from_google_sheet()
    seller_index_group = seller_index.groupby([seller_index['GP Account Owner']])
    seller_index_result = seller_index_group.agg({'GP Acc Created at M-1': 'sum',
                                                  'GP Acc Created at M-2': 'sum',
                                                  'GP Acc Created at M-3': 'sum'})
    seller_index_result = pd.DataFrame(seller_index_result).reset_index()
    upload_dataframe_to_google_sheet(seller_index_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'Initial # of shops')


def calculate_new_shops_with_gp_acc_owner():

    new_shop_index = get_new_shop_index()

    # 上传MTD New Shops
    new_shop_index_MTD = new_shop_index[(new_shop_index['new_shop_date'] >= get_start_of_this_month())
                                        & (new_shop_index['new_shop_date'] <= get_end_of_this_month())]
    # new_shop_index_MTD.to_csv('D://new_shop_index.csv', sep=',')

    new_shop_index_MTD = new_shop_index_MTD[['country',
                                             'Child Account Name',
                                             'Child ShopID',
                                             'GP Account Seller Classification',
                                             'Child Account Owner',
                                             'new_shop_date',
                                             'GP Account Owner']]

    # new_shop_index_MTD.to_csv('D://new_shop_index_MTD.csv', sep=',')

    upload_dataframe_to_google_sheet(new_shop_index_MTD,
                                     '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM',
                                     'New Shop Index with GP Acc Owner')

    # 上传M-1 New Shops
    new_shop_index_M_1 = new_shop_index[(new_shop_index['new_shop_date'] >= get_start_of_last_month())
                                        & (new_shop_index['new_shop_date'] <= get_end_of_last_month())]
    # new_shop_index_M_1.to_csv('D://new_shop_index_M_1.csv', sep=',')

    new_shop_index_M_1 = new_shop_index_M_1[['country',
                                             'Child Account Name',
                                             'Child ShopID',
                                             'GP Account Seller Classification',
                                             'Child Account Owner',
                                             'new_shop_date',
                                             'GP Account Owner']]

    # new_shop_index_M_1.to_csv('D://new_shop_index_M_1.csv', sep=',')

    upload_dataframe_to_google_sheet(new_shop_index_M_1,
                                     '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM',
                                     'New Shop Index with GP Acc Owner M-1')

    # 更新last update time
    upload_last_update_time('1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM', 'Description', 'D6')

    # 所有步骤执行完后，发一封邮件
    print('\nProcess completed!')
    send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date())
                 + ' Seller Index Calculation Completed!', 'Seller Index Calculation Completed!')


def calculate_new_shops_by_date():
    new_shop_index = get_new_shop_index()

    # 添加年月
    '''
    new_shop_index['Year/Month'] = new_shop_index['Update date'].dt.year.astype(str) \
                                   + '-' + new_shop_index['Update date'].dt.month.astype(str)
                                   '''

    new_shop_index['Year'] = new_shop_index['new_shop_date'].dt.year
    new_shop_index['Month'] = new_shop_index['new_shop_date'].dt.month
    new_shop_index['Day'] = new_shop_index['new_shop_date'].dt.day

    # aggregate
    new_shop_group = new_shop_index.groupby(['Child Account Record Type', 'Year', 'Month', 'Day'])
    new_shop_result = new_shop_group.agg({'Child ShopID': 'count'})\
        .rename(columns={'Child ShopID': '# of New Shops'})\
        .reset_index()

    # new_shop_result.sort_values(['Child Account Record Type', 'Year', 'Month'], ascending=[True, False, False])

    # 上传
    upload_dataframe_to_google_sheet(new_shop_result,
                                     '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM',
                                     'New Shops by Date')

    # return new_shop_result.head(5)


if __name__ == "__main__":
    calculate_num_of_seller_in_different_stage_by_gp_acc()
    calculate_num_of_seller_by_gp_acc_owner()
    calculate_num_of_seller_shops_by_gp_acc_owner_by_country()
    calculate_new_shops_with_gp_acc_owner()
    calculate_num_of_shop_in_different_stage_by_gp_acc()
    calculate_new_shops_by_date()

