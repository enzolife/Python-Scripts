import threading
import time
import schedule
import logging
from calculate_order_gmv_by_shop import calculate_order_gmv_by_shop
from get_order_report import get_concatenated_order_report
from calculate_sku_by_shop import calculate_sku_by_shop
from get_listing_reports import get_concatenated_listing_report
from copy_files_from_intranet import *

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.info('Start of program.')


# non stop run order
def run_order():
    from_path = "\\\\10.12.50.3\\data_source\\order_csv"
    while True:
        if check_data_validation(from_path) is not False:
            if get_concatenated_order_report is not False:
                calculate_order_gmv_by_shop()
                break


# non stop run listing
def run_listing():
    from_path = "\\\\10.12.50.3\\data_source\\listing_csv"
    while True:
        if check_data_validation(from_path) is not False:
            if get_concatenated_listing_report is not False:
                calculate_sku_by_shop()
                break


# start a thread
def run_threaded(job_func):
    print("I'm running on thread %s" % threading.current_thread())
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


# schedule run
schedule.every().day.at('15:53').do(run_threaded, run_order)
schedule.every().day.at('15:53').do(run_threaded, run_listing)

while 1:
    schedule.run_pending()
    time.sleep(1)

