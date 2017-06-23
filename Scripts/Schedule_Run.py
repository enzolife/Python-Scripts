import schedule
import time
import logging
from Scripts.Calculate_Order_GMV_by_Shop import calculate_order_gmv_by_shop
from Scripts.Get_Order_Report import get_concatenated_order_report
from Scripts.Calculate_SKU_by_Shop import calculate_sku_by_shop
from Scripts.Get_Listing_Reports import get_concatenated_listing_report
from Scripts.Get_Google_Sheets import get_certain_google_sheets


# 先不停的while true
def non_stop_calculate_order_gmv_by_shop():
    while True:
        calculate_order_gmv_by_shop()
        if get_concatenated_order_report() is not False:
            break

# log
logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# log info
logging.info('Running Calculation')

# schedule run by minute
schedule.every(1).minutes.do(calculate_order_gmv_by_shop)
schedule.every(1).minutes.do(calculate_sku_by_shop)

while True:
    schedule.run_pending()
    time.sleep(1)



