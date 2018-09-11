import threading
import time
import schedule
import logging
from get_google_sheets import get_certain_google_sheets

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.info('Start of program.')


# start a thread
def run_threaded(job_func):
    print("I'm running on thread %s" % threading.current_thread())
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


# download new shop tracker
def download_new_shop_tracker():
    list_of_google_sheet_name = [
    {"doc": "New Shop Tracker"}
    ]
    output_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
                  'Shopee 2016.4.12\\2016.8.28 Seller Index Data\\'
    selected_sheet = ['SG', 'MY', 'TW', 'ID', 'TH']
    get_certain_google_sheets(list_of_google_sheet_name, output_path, selected_sheet)


# download seller index
def download_seller_index():
    list_of_google_sheet_name = [
    {"doc": "Seller_Index_from_Salesforce"}
    ]
    output_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
                  'Shopee 2016.4.12\\2016.8.28 Seller Index Data\\'
    selected_sheet = ['Raw_Seller_Index']
    get_certain_google_sheets(list_of_google_sheet_name, output_path, selected_sheet)


# download staff contact list
def download_contact_list():
    list_of_google_sheet_name = [
    {"doc": "2017.6.28 Enzo Staff Contact List"}
    ]
    output_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
                  'Shopee 2016.4.12\\2016.12.30 员工信息表\\'
    selected_sheet = ['sheet1']
    get_certain_google_sheets(list_of_google_sheet_name, output_path, selected_sheet)


# schedule run
schedule.every().day.at('16:00').do(run_threaded, download_new_shop_tracker)
schedule.every().day.at('16:00').do(run_threaded, download_seller_index)
schedule.every().day.at('16:00').do(run_threaded, download_contact_list)

while 1:
    schedule.run_pending()
    time.sleep(1)
