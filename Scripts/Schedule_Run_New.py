import logging
from multiprocessing import Pool
from multiprocessing import Process
import schedule
from Scripts.Calculate_Order_GMV_by_Shop import calculate_order_gmv_by_shop
from Scripts.Calculate_SKU_by_Shop import calculate_sku_by_shop
from Scripts.Copy_Files_from_Intranet import *
from Scripts.Get_Listing_Reports import get_concatenated_listing_report
from Scripts.Get_Order_Report import get_concatenated_order_report

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


# to run list
def running_list(i):
    to_run_list = {0: run_order, 1: run_listing}
    return to_run_list[i]


def schedule_run():
    print('Parent process %s.' % os.getpid())
    p = Pool(4)
    p.apply_async(run_order)
    p.apply_async(run_listing)
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')


if __name__ == '__main__':
    # schedule run
    schedule.every().day.at('12:00').do(schedule_run)

    while 1:
        schedule.run_pending()
        time.sleep(1)
