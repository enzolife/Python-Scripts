import logging
from multiprocessing import Pool
import schedule
from Calculate_BD_Index import *
from Calculate_Seller_Index import *
from Calculate_Local_Stat import *
from Calculate_Local_Category_Stat import *
from Calculate_Local_MY_Shocking_Sale import *
from Copy_Files_from_Intranet import *
from calculate_order_performance import calculate_order_performance
from calculate_listing_performance import calculate_listing_performance
from calculate_shipping_performance import calculate_shipping_performance

today_date = get_today_date()


logging.basicConfig(filename='shopee_schedule_run_log ' + str(today_date) + '.txt',
                    level=logging.INFO,
                    format=' %(asctime)s - %(levelname)s - %(message)s')
logging.info('Start of program.')


# non stop run order
def run_order():
    calculate_order_performance()


# non stop run listing
def run_listing():
    calculate_listing_performance()


# non stop run pricing
# def run_pricing():

def run_shipping():
    calculate_shipping_performance()


def run_bd_index():
    calculate_num_of_leads_claimed()
    calculate_num_of_leads_by_date()
    calculate_num_of_leads_claimed_by_week()
    calculate_num_of_cb_leads_by_lead_gen()
    calculate_num_of_tb_leads_by_lead_gen()
    calculate_num_of_cb_leads_by_lead_gen_small_leads()
    calculate_num_of_tb_leads_by_lead_gen_tb_sh_sa()
    upload_bd_performance()


def run_seller_index():
    calculate_num_of_seller_in_different_stage_by_gp_acc()
    calculate_num_of_seller_by_gp_acc_owner()
    calculate_num_of_seller_shops_by_gp_acc_owner_by_country()
    calculate_new_shops_with_gp_acc_owner()
    calculate_num_of_shop_in_different_stage_by_gp_acc()
    calculate_new_shops_by_date()


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


def schedule_run_8():
    print('Parent process %s.' % os.getpid())
    p = Pool(1)
    p.apply_async(run_shipping)
    logging.info('Waiting for all subprocesses done...')
    p.close()
    # time.sleep(43200)
    # p.terminate()
    p.join()
    logging.info('Shipping stats subprocesses done. ')


if __name__ == '__main__':
    # schedule run
    schedule.every().day.at('13:00').do(schedule_run_1)  # seller index
    schedule.every().day.at('16:00').do(schedule_run_2)  # bd index
    # schedule.every().day.at('15:00').do(schedule_run_3)  # pricing
    schedule.every().day.at('16:00').do(schedule_run_4)  # order
    schedule.every().day.at('17:30').do(schedule_run_5)  # listing
    schedule.every().day.at('10:30').do(schedule_run_6)  # local order stat
    # schedule.every().day.at('18:00').do(schedule_run_7)  # local cat stat
    schedule.every().day.at('18:30').do(schedule_run_8)  # shipping

    while 1:
        schedule.run_pending()
        time.sleep(1)
