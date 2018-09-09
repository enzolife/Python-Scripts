from get_gmail_config import *
from get_google_sheets import *
from get_particular_date import *


def calculate_local_category_stat():
    # 首先，搜索Daily Sub-Category Detailed Report的最新邮件，获取最新邮件的msg_id
    search_message = ListMessagesMatchingQuery('me',
                                               'from:(nanzheng.lin@shopee.com) Daily Sub-category Detailed Report',
                                               )
    last_search_message_id = search_message[0]['id']
    print('Search completed.')

    # 然后，通过msg_id，找到附件并下载，同时获得第一个Dataframe
    local_cat_sku_data_frame = GetMultiAttachments('me',
                                                   last_search_message_id,
                                                   'D:\\Program Files (x86)\\百度云同步盘\\Dropbox'
                                                   '\\Shopee 2016.4.12\\2017.8.2 Local Stat\\',
                                                   ['Total_Local_CB_Cumulative_SKUs.csv',
                                                    'Total_Local_CB_30day_gross_orders.csv'],
                                                   1
                                                   )

    # 然后，通过msg_id，找到附件并下载，同时获得第二个Dataframe
    local_cat_order_data_frame = GetMultiAttachments('me',
                                                     last_search_message_id,
                                                     'D:\\Program Files (x86)\\百度云同步盘\\Dropbox'
                                                     '\\Shopee 2016.4.12\\2017.8.2 Local Stat\\',
                                                     ['Total_Local_CB_Cumulative_SKUs.csv',
                                                      'Total_Local_CB_30day_gross_orders.csv'],
                                                     2
                                                     )

    print('Attachment download & create data frame completed.')

    # 两个data frame合并
    local_cat_stat = pd.merge(local_cat_sku_data_frame,
                              local_cat_order_data_frame,
                              how='left',
                              left_on=['Country', 'Category', 'Subcategory'],
                              right_on=['Country', 'Category', 'sub_category'])

    # 上传到google sheet
    upload_dataframe_to_google_sheet(local_cat_stat,
                                     '131OUcYeYM42HGnQ5gjvKf3o_kZSf6k9LzVFMWHWFnKM',
                                     'local_cat_stat')

    print('Upload to google sheet completed.')

    # 更新相关表的last update time
    upload_last_update_time('131OUcYeYM42HGnQ5gjvKf3o_kZSf6k9LzVFMWHWFnKM', 'Description', 'D4')

    # 发送提醒邮件
    print('\nProcess completed!')
    send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date()) +
                 ' Local vs CB Category Data is uploaded!', 'Local vs CB Category Data is uploaded!')


if __name__ == "__main__":
    calculate_local_category_stat()
