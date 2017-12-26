from Scripts.Get_Gmail_Config import *
from Scripts.Get_Google_Sheets import *
from Scripts.Get_Particular_Date import *


def calculate_local_stat():
    # 首先，搜索CNCB vs Country stats的最新邮件，获取最新邮件的msg_id
    search_message = ListMessagesMatchingQuery('me',
                                               'from:(mingjie.lyu@shopee.com) subject:(cncb vs country) -weekly '
                                               'has:attachment',
                                               50
                                               )
    last_search_message_id = search_message[0]['id']
    print('Search completed.')

    # 然后，通过msg_id，找到附件并下载，同时获得一个data_frame
    local_stat_data_frame = GetAttachments('me',
                                           last_search_message_id,
                                           'D:\\Program Files (x86)\\百度云同步盘\\Dropbox'
                                           '\\Shopee 2016.4.12\\2017.8.2 Local Stat\\',
                                           'cb_vs_country.csv',
                                           1
                                           )
    print('Attachment download & create data frame completed.')

    # 最后，上传到google sheet
    upload_dataframe_to_google_sheet(local_stat_data_frame,
                                     '1uiGjcszIQfJ76Rct2GMpQRgmMyv32ZVaO7xNvxMfD9U',
                                     '90 Days Order')
    print('Upload to google sheet completed.')

    # 更新相关表的last update time
    upload_last_update_time('1uiGjcszIQfJ76Rct2GMpQRgmMyv32ZVaO7xNvxMfD9U', 'Description', 'D4')

    # 发送提醒邮件
    print('\nProcess completed!')
    send_message('enzo.kuang@shopee.com', '[Notices] ' + str(get_today_date()) +
                 ' CNCB vs Country Data is uploaded!', 'CNCB vs Country Data is uploaded!')

if __name__ == "__main__":
    calculate_local_stat()
