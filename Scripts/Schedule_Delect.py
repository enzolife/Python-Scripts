import threading
import schedule
import logging
from Scripts.Delete_Files_in_Folder import *

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.info('Start of program.')


# start a thread
def run_threaded(job_func):
    print("I'm running on thread %s" % threading.current_thread())
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


# Delete order report
def delete_order_report():
    path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                        "Shopee 2016.4.12\\2016.4.23 Data Visualization\\Order"
    delete_all_file_in_folder(path)


# Delete listing report
def delete_listing_report():
    path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                        "Shopee 2016.4.12\\2016.4.23 Data Visualization\\Listing"
    delete_all_file_in_folder(path)


# Delete pricing report
def delete_pricing_report():
    path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                        "Shopee 2016.4.12\\2016.4.23 Data Visualization\\Pricing"
    delete_all_file_in_folder(path)


# Delete pricing report
def delete_product_view_report():
    path = "D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\" \
                        "Shopee 2016.4.12\\2016.4.23 Data Visualization\\ProductView"
    delete_all_file_in_folder(path)


# schedule run
schedule.every().day.at('10:30').do(run_threaded, delete_order_report)
schedule.every().day.at('10:30').do(run_threaded, delete_listing_report)
schedule.every().day.at('10:30').do(run_threaded, delete_pricing_report)
schedule.every().day.at('10:30').do(run_threaded, delete_product_view_report)

while 1:
    schedule.run_pending()
    time.sleep(1)
