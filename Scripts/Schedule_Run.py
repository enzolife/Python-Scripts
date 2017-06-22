import schedule
import time
import logging
from Scripts.Calculate_Order_GMV_by_Shop import calculate_order_gmv_by_shop
from Scripts.Calculate_SKU_by_Shop import calculate_sku_by_shop

# log
logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')

# log info
logging.info('Running Calculation')

# schedule run
schedule.every(1).minutes.do(calculate_order_gmv_by_shop)
schedule.every(1).minutes.do(calculate_sku_by_shop)

while True:
    schedule.run_pending()
    time.sleep(1)
