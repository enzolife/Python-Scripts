from Scripts.Get_Gmail_Config import *
from Scripts.Get_Google_Sheets import *
from Scripts.Get_Particular_Date import *


def calculate_local_my_shocking_sale():
    # 首先，搜索Daily Sub-Category Detailed Report的最新邮件，获取最新邮件的msg_id
    search_message = ListMessagesMatchingQuery('me',
                                               'from:(menghua.sun@shopee.com) subject:(Shocking Sale Daily Report Data)',
                                               )
    last_search_message_id = search_message[0]['id']
    print('Search completed.')

    # 然后，通过msg_id，找到附件并下载，同时获得第一个Dataframe
    local_my_shocking_sale = GetSelectedMultiAttachments('me',
                                                         last_search_message_id,
                                                         'D:\\Program Files (x86)\\百度云同步盘\\Dropbox'
                                                         '\\Shopee 2016.4.12\\2017.8.2 Local Stat\\',
                                                         'local_my_shocking_sale_1.csv',
                                                         1,
                                                         1
                                                         )

    local_my_shocking_sale = local_my_shocking_sale[local_my_shocking_sale['cb_option'] == 1]

    # 上传到google sheet
    upload_dataframe_to_google_sheet(local_my_shocking_sale,
                                     '1qNLHH3Iqwfm_gNcz3NOYVZl9dPYmaI2jOmk4T8ttu4k',
                                     'MY Shocking Sale')

    print('Upload to google sheet completed.')

    # 更新相关表的last update time
    upload_last_update_time('1qNLHH3Iqwfm_gNcz3NOYVZl9dPYmaI2jOmk4T8ttu4k', 'MY Shocking Sale', 'R1')

    # 发送提醒邮件
    print('\nProcess completed!')
    send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date()) +
                 ' MY Shocking Sale Daily Report is uploaded!', 'MY Shocking Sale Daily Report is uploaded!')


if __name__ == "__main__":
    calculate_local_my_shocking_sale()
