import logging
import os
import schedule
import time
from multiprocessing import Pool
from Scripts.Enzo_Get_SMT_Search_Result import get_smt_search_result


logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')
logging.info('Start of program.')


def schedule_run_1():
    print('Parent process %s.' % os.getpid())
    p = Pool(1)
    p.apply_async(get_smt_search_result)
    logging.info('Waiting for all subprocesses done...')
    p.close()
    # time.sleep(43200)
    # p.terminate()
    p.join()
    logging.info('All subprocesses done. ')


if __name__ == '__main__':
    # schedule run
    schedule.every().hour.do(schedule_run_1)

    while 1:
        schedule.run_pending()
        time.sleep(1)