import pandas as pd
from Scripts.Get_Seller_Index import get_gp_acc_index, get_seller_index_from_google_sheet
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
    seller_index = get_seller_index_from_google_sheet()

    book_name = "New Shop Tracker"
    selected_sheet = ['SG', 'MY', 'TW', 'ID', 'TH', 'PH']
    list_ = []
    for country_sheet in selected_sheet:
        country_new_shop_index = get_certain_google_sheets_to_dataframe(book_name, country_sheet)
        list_.append(country_new_shop_index)

    new_shop_index = pd.concat(list_)
    new_shop_index.to_csv('D://Program Files (x86)//百度云同步盘//Dropbox//Shopee 2016.4.12//'
                          '2016.8.28 Seller Index Data//new_shop_index.csv', sep=',')
    new_shop_index['Update date'] = pd.to_datetime(new_shop_index['Update date'])

    # 上传MTD New Shops
    new_shop_index_MTD = new_shop_index[(new_shop_index['Update date'] >= get_start_of_this_month())]
    new_shop_index_MTD.to_csv('D://new_shop_index.csv', sep=',')

    new_shop_index_MTD = pd.merge(new_shop_index_MTD, seller_index, how='left', left_on='Shop id',
                                  right_on='Child ShopID')

    new_shop_index_MTD = new_shop_index_MTD[['Site',
                                             'Shop name',
                                             'Shop id',
                                             'Shop url',
                                             'PIC',
                                             'Update date',
                                             'GP Account Owner']]

    new_shop_index_MTD.to_csv('D://new_shop_index_MTD.csv', sep=',')

    upload_dataframe_to_google_sheet(new_shop_index_MTD,
                                     '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM',
                                     'New Shop Index with GP Acc Owner')

    # 上传M-1 New Shops
    new_shop_index_M_1 = new_shop_index[(new_shop_index['Update date'] >= get_start_of_last_month())
                                        & (new_shop_index['Update date'] <= get_end_of_last_month())]
    new_shop_index_M_1.to_csv('D://new_shop_index_M_1.csv', sep=',')

    new_shop_index_M_1 = pd.merge(new_shop_index_M_1, seller_index, how='left', left_on='Shop id',
                                  right_on='Child ShopID')

    new_shop_index_M_1 = new_shop_index_M_1[['Site',
                                             'Shop name',
                                             'Shop id',
                                             'Shop url',
                                             'PIC',
                                             'Update date',
                                             'GP Account Owner']]

    new_shop_index_M_1.to_csv('D://new_shop_index_M_1.csv', sep=',')

    upload_dataframe_to_google_sheet(new_shop_index_M_1,
                                     '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM',
                                     'New Shop Index with GP Acc Owner M-1')

    # 更新last update time
    upload_last_update_time('1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM', 'Description', 'D6')

    # 所有步骤执行完后，发一封邮件
    print('\nProcess completed!')
    send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date())
                 + ' Seller Index Calculation Completed!', 'Seller Index Calculation Completed!')


if __name__ == "__main__":
    calculate_num_of_seller_in_different_stage_by_gp_acc()
    calculate_num_of_seller_by_gp_acc_owner()
    calculate_new_shops_with_gp_acc_owner()
    calculate_num_of_shop_in_different_stage_by_gp_acc()
