from Get_Lead_Index import get_lead_index_from_google_sheet
from Get_Google_Sheets import upload_dataframe_to_google_sheet, upload_last_update_time
from Get_Seller_Index import get_seller_index_from_google_sheet
from Get_Particular_Date import *
from Get_Gmail_Config import send_message
from Get_Seller_Index import get_new_shop_index
import pandas as pd
import numpy as np


def get_bd_index_config():
    bd_index = get_lead_index_from_google_sheet()
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

# Claimed W+1 Account Opening Report
def calculate_num_of_leads_claimed():
    bd_index = get_bd_index_config()

    start_of_w_2 = get_last_monday() + datetime.timedelta(days=-7)
    end_of_w_2 = get_last_sunday() + datetime.timedelta(days=-7)

    # 计算w-2 # of leads claimed by lead owner
    bd_index_claimed_date_is_w_2 = bd_index[(bd_index['Claimed Date'] >= start_of_w_2)
                                            & (bd_index['Claimed Date'] <= end_of_w_2)]

    bd_index_claimed_date_is_w_2_group = bd_index_claimed_date_is_w_2.groupby('Sales Lead: Owner Name')
    bd_index_claimed_date_is_w_2_result = bd_index_claimed_date_is_w_2_group.agg({'Sales Lead: ID': 'count'}) \
        .reset_index()

    # 计算w-1 new shops by gp acc
    new_shop_index = get_new_shop_index()
    new_shop_index_is_w_1 = new_shop_index[(new_shop_index['new_shop_date'] >= get_last_monday())
                                           & (new_shop_index['new_shop_date'] <= get_last_sunday())]

    # bd index merge new shop index
    new_shop_index_is_w_1_group = new_shop_index_is_w_1.groupby('GP Account Lead Name')
    new_shop_index_is_w_1_result = new_shop_index_is_w_1_group.agg({'Child ShopID': 'count'}).reset_index()

    bd_index_merge_new_shop_index = pd.merge(bd_index_claimed_date_is_w_2, new_shop_index_is_w_1_result, how='inner',
                                             left_on=['Sales Lead: Lead Name'],
                                             right_on=['GP Account Lead Name'])

    bd_index_merge_new_shop_index_group = bd_index_merge_new_shop_index.groupby('Sales Lead: Owner Name')
    bd_index_merge_new_shop_index_result = bd_index_merge_new_shop_index_group.agg({'Sales Lead: ID': 'count'}) \
        .reset_index()

    # final table
    final_result = pd.merge(bd_index_claimed_date_is_w_2_result, bd_index_merge_new_shop_index_result, how='left',
                            left_on=['Sales Lead: Owner Name'],
                            right_on=['Sales Lead: Owner Name'])

    final_result = final_result.rename(columns={'Sales Lead: ID_x': '# of leads claimed at W-2',
                                                'Sales Lead: ID_y': '# of leads with shop opened at W-1'})

    final_result['% opened'] = final_result['# of leads with shop opened at W-1'] \
                               / final_result['# of leads claimed at W-2']

    final_result = final_result.sort('# of leads claimed at W-2', ascending=False)

    # 上传结果
    upload_dataframe_to_google_sheet(final_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'Claimed W-1 Account Opening Report')

    return final_result


# Account Opening Aging Report
def calculate_num_of_leads_claimed_by_week():
    bd_index = get_bd_index_config()
    new_shop_index = get_new_shop_index()

    # 计算每个gp account lead name有多少个new shop
    new_shop_index_group = new_shop_index.groupby('GP Account Lead Name')
    new_shop_index_result = new_shop_index_group.agg({'Child ShopID': 'count',
                                                      'new_shop_date': 'min'}) \
        .rename(columns={'Child ShopID': '# of new shops',
                         'new_shop_date': 'first shop created date'}) \
        .reset_index()

    # merge
    bd_index = pd.merge(bd_index, new_shop_index_result, how='left',
                        left_on=['Sales Lead: Lead Name'],
                        right_on=['GP Account Lead Name'])

    # select only claimed lead
    bd_index = bd_index[bd_index['Claimed Date'] >= datetime.date(1900, 1, 1)]

    # today
    bd_index['Today Date'] = get_today_date()
    bd_index['Today Date'] = pd.to_datetime(bd_index['Today Date'])

    # opening lead time
    bd_index['Opening Lead Time'] = np.where(bd_index['# of new shops'] > 0,
                                             (bd_index['first shop created date'] - bd_index['Claimed Date']).dt.days,
                                             np.NAN)

    # delete opening lead time < 0
    bd_index['Opening Lead Time'] = np.where(bd_index['Opening Lead Time'] >= 0,
                                             bd_index['Opening Lead Time'],
                                             np.NAN)

    # pending time
    bd_index['Lead Pending Time'] = np.where((bd_index['first shop created date'] >= datetime.date(1900, 1, 1)),
                                             np.NAN,
                                             (bd_index['Today Date'] - bd_index['Claimed Date']).dt.days)

    # add week num & year
    '''
    bd_index['Year-Week'] = 'W' + bd_index['Claimed Date'].dt.week.apply(str)\
                            + '-' + bd_index['Claimed Date'].dt.year.apply(str)
                            '''

    bd_index['Year'] = bd_index['Claimed Date'].dt.year
    bd_index['Week'] = bd_index['Claimed Date'].dt.week

    # aggregate
    bd_index_group = bd_index.groupby(['Year', 'Week'])
    bd_index_result = bd_index_group.agg({'Sales Lead: Lead Name': 'count',
                                          'GP Account Lead Name': 'count',
                                          'Opening Lead Time': 'mean',
                                          'Lead Pending Time': 'mean'}) \
        .rename(columns={'Sales Lead: Lead Name': 'Total # lead claimed',
                         'GP Account Lead Name': '# lead with opened shop',
                         'Opening Lead Time': 'Average opening lead time (claimed date to first shop opened date)',
                         'Lead Pending Time': 'Average pending time (claimed date to TODAY)'}) \
        .reset_index()

    # add supportive columns
    bd_index_result['% opened'] = bd_index_result['# lead with opened shop'] / bd_index_result['Total # lead claimed']
    bd_index_result['# lead not yet opened shop'] = bd_index_result['Total # lead claimed'] \
                                                    - bd_index_result['# lead with opened shop']

    bd_index_result['% NOT opened'] = bd_index_result['# lead not yet opened shop'] \
                                      / bd_index_result['Total # lead claimed']

    # re-arrange columns
    bd_index_result = bd_index_result.reindex(columns=['Year',
                                                       'Week',
                                                       'Total # lead claimed',
                                                       '# lead with opened shop',
                                                       '% opened',
                                                       'Average opening lead time '
                                                       '(claimed date to first shop opened date)',
                                                       '# lead not yet opened shop',
                                                       '% NOT opened',
                                                       'Average pending time (claimed date to TODAY)'])

    bd_index_result.sort(['Year', 'Week'], ascending=[1, 1])

    # 上传结果
    upload_dataframe_to_google_sheet(bd_index_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'Account Opening Aging Report')

    return bd_index_result


# CB SA Target Tracking
def calculate_num_of_cb_leads_by_lead_gen():
    bd_index = get_bd_index_config()

    # 判断CB
    bd_index = bd_index[bd_index['Seller Classification'].str.contains('CB', na=False)]

    '''
    # 选择日期范围，MTD
    bd_index = bd_index[(bd_index['Sales Lead: Created Date'] >= get_start_of_this_month())
                        & (bd_index['Sales Lead: Created Date'] <= get_yesterday_date())]
    '''

    # 判断Big/Medium/Small
    super_big_medium_lead_owner = ['Shelly Zhuo', 'Ivan Wu', 'Cindy Jin', 'Ki Wong',
                                   'Vicky Liu', 'Yoyo Zhao', 'Nikki Yu', 'Boey Peng', 'Jun Li',
                                   'Christine Tang', 'Zheng Kai']

    '''
    # 使用select语言
    leads_conditions = [
        (bd_index['Sales Lead: Owner Name'].isin(big_medium_lead_owner)) & (bd_index['Lead Size'] == 'Super'),
        (bd_index['Sales Lead: Owner Name'].isin(big_medium_lead_owner)) & (bd_index['Lead Size'] == 'Big'),
        (bd_index['Sales Lead: Owner Name'].isin(big_medium_lead_owner)) & (bd_index['Lead Size'] == 'Medium'),
        (bd_index['Sales Lead: Owner Name'].isin(big_medium_lead_owner)) & (bd_index['Lead Size'] == 'Small')
    ]
    leads_choices = ['Super', 'Big', 'Medium', 'Medium']
    bd_index['Actual_Leads_Size'] = np.select(leads_conditions, leads_choices, default='Small')
    '''

    # 首要条件，lead owner != lead gen
    lead_owner_not_lead_gen = (bd_index['Sales Lead: Owner Name'] != bd_index['Lead Gen'])

    # 次要条件，lead owner为super_big_medium_lead_owner
    lead_owner_is_kam = (bd_index['Sales Lead: Owner Name'].isin(super_big_medium_lead_owner))
    lead_owner_not_kam = (~bd_index['Sales Lead: Owner Name'].isin(super_big_medium_lead_owner))

    # 日期条件
    lead_claimed_date_mtd = ((bd_index['Claimed Date'] >= get_start_of_this_month())
                             & (bd_index['Claimed Date'] <= get_yesterday_date()))
    lead_transferred_date_mtd = ((bd_index['Date Transferred to Onboarding Queue'] >= get_start_of_this_month())
                                 & (bd_index['Date Transferred to Onboarding Queue'] <= get_yesterday_date()))
    '''
    lead_claimed_date_mtd = ((bd_index['Claimed Date'] >= datetime.date(2018, 2, 1))
                             & (bd_index['Claimed Date'] <= datetime.date(2018, 2, 28)))
    lead_transferred_date_mtd = ((bd_index['Date Transferred to Onboarding Queue'] >= datetime.date(2018, 2, 1))
                                 & (bd_index['Date Transferred to Onboarding Queue'] <= datetime.date(2018, 2, 28)))
    '''

    # Actual Super/Big/Medium
    bd_index['Actual_Selected_Leads'] = np.where((lead_owner_not_lead_gen & lead_claimed_date_mtd & lead_owner_is_kam),
                                                 bd_index['Lead Size'], '')

    # Actual Small
    bd_index['Actual_Small_Leads'] = np.where((lead_owner_not_lead_gen & lead_transferred_date_mtd & lead_owner_not_kam)
                                              , 'Small', '')

    bd_index.to_csv('D:\\bd_index.csv', sep=',')

    # group by
    bd_index_group = bd_index.groupby(['Lead Gen', 'Actual_Selected_Leads', 'Actual_Small_Leads'])
    bd_index_result = bd_index_group.agg({'Sales Lead: ID': 'count'}) \
        .rename(columns={'Sales Lead: ID': '# of leads'}) \
        .reset_index()

    # upload to bd performance report
    upload_dataframe_to_google_sheet(bd_index_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'mtd_num_of_cb_leads_by_lead_gen')

    return bd_index_result


# TB SA Target Tracking
def calculate_num_of_tb_leads_by_lead_gen():
    # MTD
    bd_index = get_bd_index_config()

    # 判断TB
    bd_index = bd_index[bd_index['Seller Classification'].str.contains('Taobao', na=False)]

    # 选择日期范围，MTD
    bd_index = bd_index[(bd_index['Date Transferred to Onboarding Queue'] >= get_start_of_this_month())
                        & (bd_index['Date Transferred to Onboarding Queue'] <= get_yesterday_date())]

    # 判断Actual Leads
    bd_index['Actual_Leads'] = np.where((bd_index['Sales Lead: Owner Name'] != bd_index['Lead Gen']),
                                        'Actual Lead', 'Not Actual Lead')
    bd_index = bd_index[bd_index['Actual_Leads'] == 'Actual Lead']

    # group by
    bd_index_group = bd_index.groupby(['Lead Gen'])
    bd_index_result = bd_index_group.agg({'Sales Lead: ID': 'count'}) \
        .rename(columns={'Sales Lead: ID': '# of leads'}) \
        .reset_index()

    # upload to bd performance report
    upload_dataframe_to_google_sheet(bd_index_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'mtd_num_of_tb_leads_by_lead_gen')

    # WTD/W-1
    bd_index = get_bd_index_config()

    # 判断TB
    bd_index = bd_index[bd_index['Seller Classification'].str.contains('Taobao', na=False)]

    # 选择日期范围
    bd_index = bd_index[(bd_index['Date Transferred to Onboarding Queue'] >= get_last_monday())
                        & (bd_index['Date Transferred to Onboarding Queue'] <= get_yesterday_date())]

    # 判断Actual Leads
    bd_index['Actual_Leads'] = np.where((bd_index['Sales Lead: Owner Name'] != bd_index['Lead Gen']),
                                        'Actual Lead', 'Not Actual Lead')

    # WTD/W-1 Leads
    bd_index['WTD Lead'] = np.where(
        ((bd_index['Actual_Leads'] == 'Actual Lead') & (
                bd_index['Date Transferred to Onboarding Queue'] >= get_this_monday())
         & (bd_index['Date Transferred to Onboarding Queue'] <= get_yesterday_date())), 1, 0)
    bd_index['W-1 Lead'] = np.where(
        ((bd_index['Actual_Leads'] == 'Actual Lead') & (
                bd_index['Date Transferred to Onboarding Queue'] >= get_last_monday())
         & (bd_index['Date Transferred to Onboarding Queue'] <= get_last_sunday())), 1, 0)

    # group by
    bd_index_group = bd_index.groupby(['Lead Gen'])
    bd_index_result = bd_index_group.agg({'WTD Lead': 'sum', 'W-1 Lead': 'sum'}) \
        .reset_index()

    # upload to bd performance report
    upload_dataframe_to_google_sheet(bd_index_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'wtd_w_1_num_of_tb_leads_by_lead_gen')

    return bd_index_result


# CB SA Target Tracking (Small Leads)
def calculate_num_of_cb_leads_by_lead_gen_small_leads():
    seller_index = get_seller_index_from_google_sheet()

    # GP Acc. Create Date >= 2018/3/1
    gp_account_create_date_filter = seller_index['GP Account Shopee Account Created Date'] >= datetime.date(2018, 3, 1)
    seller_index = seller_index[gp_account_create_date_filter]

    # date transfer from onboarding team is current month
    date_transfer_date_filter = (seller_index['Date Transferred From Onboarding Team'] >= get_start_of_this_month()) \
                                & (seller_index['Date Transferred From Onboarding Team'] <= get_yesterday_date())
    seller_index = seller_index[date_transfer_date_filter]

    # GP Acc. Owner is Mei Wenjuan or Stephen Luo
    gp_owner_filter = (seller_index['GP Account Owner'] == 'Mei Wenjuan') |\
                      (seller_index['GP Account Owner'] == 'Steven Luo')
    seller_index = seller_index[gp_owner_filter]

    # Seller type is not TB
    seller_type_filter = ~seller_index['GP Account Seller Classification'].str.contains('Taobao')
    seller_index = seller_index[seller_type_filter]
    # print(seller_index.head())
    seller_index.to_csv("D://cb_sa_small_leads.csv", sep=',')

    # calculation
    seller_index_group = seller_index.groupby(['Lead Gen'])
    seller_index_result = seller_index_group.agg({'Sales Lead: ID': 'nunique'}).reset_index()

    # upload to bd performance report
    upload_dataframe_to_google_sheet(seller_index_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'mtd_num_of_cb_leads_by_lead_gen_small_leads')

    return None


# TB SA Target Tracking (By Focus / Non-focus Cat)
def calculate_num_of_tb_leads_by_lead_gen_small_leads():
    seller_index = get_seller_index_from_google_sheet()

    # date transfer from onboarding team is current month
    date_transfer_date_filter = (seller_index['Date Transferred From Onboarding Team'] >= get_start_of_this_month()) \
                                & (seller_index['Date Transferred From Onboarding Team'] <= get_yesterday_date())
    seller_index = seller_index[date_transfer_date_filter]

    # GP Acc. Owner is Mei Wenjuan
    gp_owner_filter = seller_index['GP Account Owner'] == 'Mei Wenjuan'
    seller_index = seller_index[gp_owner_filter]
    # print(seller_index.head())

    # Seller type is TB
    seller_type_filter = seller_index['GP Account Seller Classification'].str.contains('Taobao')
    seller_index = seller_index[seller_type_filter]
    # print(seller_index.head())

    # Focus & Non-focus Category
    focus_cat_list = ['Home & Living',
                      'Toys, Kids & Babies',
                      'Toys. Kids & Babies']
    seller_index['focus_cat_seller'] = np.where(seller_index['Primary Category_x'].isin(focus_cat_list),
                                                seller_index['Sales Lead: ID'], '')
    seller_index['non_focus_cat_seller'] = np.where(~seller_index['Primary Category_x'].isin(focus_cat_list),
                                                    seller_index['Sales Lead: ID'], '')
    # print(seller_index.head())

    # calculation
    seller_index_group = seller_index.groupby(['Lead Gen'])
    seller_index_result = seller_index_group.agg({'focus_cat_seller': 'count',
                                                  'non_focus_cat_seller': 'count'}).reset_index()
    # print(seller_index_result)

    # upload to bd performance report
    upload_dataframe_to_google_sheet(seller_index_result,
                                     '1A6sGYtEV2_IbzjxjSGIixFFre0l-fY5C0T8Qt34IiB8',
                                     'mtd_num_of_tb_leads_by_lead_gen_focus_non_focus')

    return None


if __name__ == '__main__':
    '''
    calculate_num_of_leads_claimed()
    calculate_num_of_leads_by_date()
    calculate_num_of_leads_claimed_by_week()
    calculate_num_of_cb_leads_by_lead_gen()
    calculate_num_of_tb_leads_by_lead_gen()
    upload_bd_performance()

    '''
    # num_of_tb_leads_by_lead_gen = calculate_num_of_tb_leads_by_lead_gen()
    # print(num_of_tb_leads_by_lead_gen)
    # selected_column = ['Lead Size', 'Sales L ead: Owner Name', 'Actual_Leads_Size']
    # num_of_cb_leads_by_lead_gen.to_csv("D://test_lead.csv", sep=',')

    calculate_num_of_cb_leads_by_lead_gen_small_leads()
    # calculate_num_of_tb_leads_by_lead_gen_small_leads()
