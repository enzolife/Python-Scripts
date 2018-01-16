import logging
from multiprocessing import Pool
import schedule
from Scripts.Calculate_Order_GMV_by_Shop import calculate_order_gmv_by_shop
from Scripts.Calculate_SKU_by_Shop_New_New import calculate_sku_by_shop
from Scripts.Calculate_SKU_by_Cat_Product import calculate_sku_by_cat_product
from Scripts.Calculate_Pricing_by_Cat_Product import calculate_pricing_by_cat_product
from Scripts.Calculate_BD_Index import *
from Scripts.Calculate_Seller_Index import *
from Scripts.Calculate_Local_Stat import *
from Scripts.Calculate_Local_Category_Stat import *
from Scripts.Calculate_Local_MY_Shocking_Sale import *
from Scripts.Copy_Files_from_Intranet import *
from Scripts.Get_Listing_Reports import get_concatenated_listing_report
from Scripts.Get_Order_Report import get_concatenated_order_report
from Scripts.Get_Pricing_Report import get_concatenated_pricing_report


logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.info('Start of program.')


# non stop run order
def run_order():
    from_path = "\\\\10.12.50.3\\data_source\\order_csv"
    while True:
        if check_data_validation(from_path) is True:
            copy_order_report_from_intranet()
            if get_concatenated_order_report is not False:
                calculate_order_gmv_by_shop()
                break
        else:
            time.sleep(300)


# non stop run listing
def run_listing():
    from_path = "\\\\10.12.50.3\\data_source\\listing_csv"
    while True:
        if check_data_validation(from_path) is True:
            copy_listing_report_from_intranet()
            if get_concatenated_listing_report is not False:
                calculate_sku_by_shop()
                calculate_sku_by_cat_product()
                break
        else:
            time.sleep(300)


# non stop run pricing
def run_pricing():
    from_path = "\\\\10.12.50.3\\data_source\\pricing_csv"
    while True:
        if check_data_validation(from_path) is True:
            copy_pricing_report_from_intranet()
            if get_concatenated_pricing_report is not False:
                calculate_pricing_by_cat_product()
                break
        else:
            time.sleep(300)


def run_bd_index():
    calculate_num_of_leads_claimed()
    calculate_num_of_leads_by_date()
    calculate_num_of_leads_claimed_by_week()
    upload_bd_performance()


def run_seller_index():
    calculate_num_of_seller_in_different_stage_by_gp_acc()
    calculate_num_of_seller_by_gp_acc_owner()
    calculate_new_shops_with_gp_acc_owner()
    calculate_new_shops_by_date()
    calculate_num_of_shop_in_different_stage_by_gp_acc()


def run_local_stat():
    calculate_local_stat()


def run_local_cat_stat():
    calculate_local_category_stat()
    calculate_local_my_shocking_sale()


def schedule_run_1():
    print('Parent process %s.' % os.getpid())
    p = Pool(1)
    p.apply_async(run_seller_index)
    logging.info('Waiting for all subprocesses done...')
    p.close()
    # time.sleep(43200)
    # p.terminate()
    p.join()
    logging.info('Seller Index subprocesses done. ')


def schedule_run_2():
    print('Parent process %s.' % os.getpid())
    p = Pool(1)
    p.apply_async(run_bd_index)
    logging.info('Waiting for all subprocesses done...')
    p.close()
    # time.sleep(43200)
    # p.terminate()
    p.join()
    logging.info('BD Index subprocesses done. ')


def schedule_run_3():
    print('Parent process %s.' % os.getpid())
    p = Pool(1)
    p.apply_async(run_pricing)
    logging.info('Waiting for all subprocesses done...')
    p.close()
    # time.sleep(43200)
    # p.terminate()
    p.join()
    logging.info('Pricing subprocesses done. ')


def schedule_run_4():
    print('Parent process %s.' % os.getpid())
    p = Pool(1)
    p.apply_async(run_order)
    logging.info('Waiting for all subprocesses done...')
    p.close()
    # time.sleep(43200)
    # p.terminate()
    p.join()
    logging.info('Order subprocesses done. ')


def schedule_run_5():
    print('Parent process %s.' % os.getpid())
    p = Pool(1)
    p.apply_async(run_listing)
    logging.info('Waiting for all subprocesses done...')
    p.close()
    # time.sleep(43200)
    # p.terminate()
    p.join()
    logging.info('Listing subprocesses done. ')


def schedule_run_6():
    print('Parent process %s.' % os.getpid())
    p = Pool(1)
    p.apply_async(run_local_stat)
    logging.info('Waiting for all subprocesses done...')
    p.close()
    # time.sleep(43200)
    # p.terminate()
    p.join()
    logging.info('Local stats subprocesses done. ')


def schedule_run_7():
    print('Parent process %s.' % os.getpid())
    p = Pool(1)
    p.apply_async(run_local_cat_stat)
    logging.info('Waiting for all subprocesses done...')
    p.close()
    # time.sleep(43200)
    # p.terminate()
    p.join()
    logging.info('Local Cat stats subprocesses done. ')

if __name__ == '__main__':
    # schedule run
    schedule.every().day.at('13:00').do(schedule_run_1)  # seller index
    schedule.every().day.at('16:00').do(schedule_run_2)  # bd index
    schedule.every().day.at('15:00').do(schedule_run_3)  # pricing
    schedule.every().day.at('14:00').do(schedule_run_4)  # order
    schedule.every().day.at('17:30').do(schedule_run_5)  # listing
    schedule.every().day.at('10:30').do(schedule_run_6)  # local order stat
    schedule.every().day.at('17:00').do(schedule_run_7)  # local cat stat

    while 1:
        schedule.run_pending()
        time.sleep(1)
