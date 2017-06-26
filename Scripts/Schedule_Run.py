import schedule
import time
import logging
from Scripts.Calculate_Order_GMV_by_Shop import calculate_order_gmv_by_shop
from Scripts.Get_Order_Report import get_concatenated_order_report
from Scripts.Calculate_SKU_by_Shop import calculate_sku_by_shop
from Scripts.Get_Listing_Reports import get_concatenated_listing_report
# from Scripts.Get_Google_Sheets import get_certain_google_sheets
from multiprocessing import Process
import os


# while true
def non_stop_calculate_order_gmv_by_shop():
    while True:
        calculate_order_gmv_by_shop()
        if get_concatenated_order_report() is not False:
            break


# while true
def non_stop_calculate_sku_by_shop():
    while True:
        calculate_sku_by_shop()
        if get_concatenated_listing_report() is not False:
            break


def run_job(job):
    if __name__ == '__main__':
        print('Parent process %s.' % os.getpid())
        p = Process(target=job)
        print('Child process will start.')
        p.start()
        p.join()
        print('Child process end.')

# log
logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# log info
logging.info('Running Calculation')

# schedule run by minute
schedule.every().day.at("18:51").do(run_job(non_stop_calculate_sku_by_shop))

while True:
    schedule.run_pending()
    time.sleep(1)



