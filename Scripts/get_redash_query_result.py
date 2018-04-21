import requests
import logging
import time
import pandas as pd
import numpy as np
import urllib
from Scripts.Get_Seller_Index import get_seller_index_from_google_sheet
from Scripts.Get_Local_Currency import get_local_currency
from Scripts.Get_Google_Sheets import upload_dataframe_to_google_sheet

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')


def poll_job(s, redash_url, job):
    # TODO: add timeout
    while job['status'] not in (3, 4):
        response = s.get('{}/api/jobs/{}'.format(redash_url, job['id']))
        job = response.json()['job']
        time.sleep(1)

    if job['status'] == 3:
        return job['query_result_id']

    return None


def get_fresh_query_result(redash_url: object, query_id: object, api_key: object, params: object) -> object:
    s = requests.Session()
    s.headers.update({'Authorization': 'Key {}'.format(api_key)})

    response = s.post('{}/api/queries/{}/refresh'.format(redash_url, query_id), params=params)
    if response.status_code != 200:
        raise Exception('Refresh failed.')

    result_id = poll_job(s, redash_url, response.json()['job'])

    if result_id:
        response = s.get('{}/api/queries/{}/results/{}.json'.format(redash_url, query_id, result_id))
        if response.status_code != 200:
            raise Exception('Failed getting results.')
    else:
        raise Exception('Query execution failed.')

    return pd.DataFrame(response.json()['query_result']['data']['rows'])


def get_shop_performance_by_certain_period(query_id):
    '''
    :param query_id: 994 for monthly performance / 990 for weekly performance / 1004 for yesterday performance
    :return: shop performance data_frame for certain period
    '''
    count = 1
    country_list = ["tw", "id", "my", "sg", "ph", "th", "vn"]

    execute_success = None

    while execute_success is None:
        try:
            for i in country_list:
                params = {'p_country': i}
                result = get_fresh_query_result('http://10.12.5.53',
                                                query_id,
                                                'PrsLn6Mf09MuBxBTrAEeRdT3gyqKzbG20obScoEV',
                                                params) \
                    .reset_index(drop=True)
                result['country'] = i
                if count == 1:
                    final_result = result
                else:
                    final_result = final_result.append(result)
                count += 1
            execute_success = 1
        except Exception as err:
            logging.info('An exception occurred: ' + str(err) + ', try again.')
            time.sleep(60)
            pass

    final_result = final_result.rename(columns={"shopid": "Child ShopID"})
    final_result["Child ShopID"] = final_result["Child ShopID"].convert_objects(convert_numeric=True)

    # left join seller index
    seller_index = get_seller_index_from_google_sheet()
    final_result = pd.merge(final_result, seller_index, how='left', left_on=['Child ShopID'], right_on=['Child ShopID'])

    # left join currency table
    currency_table = get_local_currency()
    currency_table['currency_name'] = currency_table['currency_name'].str.lower()
    final_result = pd.merge(final_result, currency_table, how='left', left_on=['country'], right_on=['currency_name'])

    if query_id == 994:  # monthly performance
        final_result['m-1_gmv_usd'] = final_result.iloc[:, 0] / final_result['Currency']
        final_result['mtd_gmv_usd'] = final_result.iloc[:, 4] / final_result['Currency']
    elif query_id == 990:  # weekly performance
        final_result['w-1_gmv_usd'] = final_result.iloc[:, 1] / final_result['Currency']
        final_result['wtd_gmv_usd'] = final_result.iloc[:, 5] / final_result['Currency']
    elif query_id == 1004:  # yesterday
        final_result['yesterday_gmv_usd'] = final_result.iloc[:, 3] / final_result['Currency']
    else:
        pass

    return final_result


def get_fresh_query_result_and_upload_to_google_sheet(query_id, params, sheet_id, wks_name):
    df_to_upload = get_fresh_query_result('http://10.12.5.53',
                                          query_id,
                                          'PrsLn6Mf09MuBxBTrAEeRdT3gyqKzbG20obScoEV',
                                          params)

    upload_dataframe_to_google_sheet(df_to_upload, sheet_id, wks_name)


if __name__ == '__main__':
    # print(shop_performance_by_certain_period(994).head())
    # get_shop_performance_by_certain_period(1004).to_csv('D:\\yesterday_performance.csv')
    '''
    get_90_days_order_for_each_country = get_fresh_query_result('http://10.12.5.53',
                                                                1200,
                                                                'PrsLn6Mf09MuBxBTrAEeRdT3gyqKzbG20obScoEV',
                                                                {}).set_index(['date_id', 'country'])
    get_90_days_order_for_each_country = pd.DataFrame(get_90_days_order_for_each_country).unstack().reset_index()
    get_90_days_order_for_each_country.columns = get_90_days_order_for_each_country.columns.droplevel(0)

    get_90_days_order_for_each_country.columns.values[0] = 'date_id'

    print(get_90_days_order_for_each_country)
    

    params = {'p_test': "'G00343764247'"}

    params = urllib.parse.urlencode(params)

    get_MTD_daily_order_by_gp_acc_owner_by_country \
        = get_fresh_query_result('http://10.12.5.53',
                                 1416,
                                 'PrsLn6Mf09MuBxBTrAEeRdT3gyqKzbG20obScoEV',
                                 params)

    '''
    get_fresh_query_result_and_upload_to_google_sheet(1948, {},
                                                      '1XIY1juem3rDGNf2P8MyTc8W-QpT1aK4pAl6yHRkCARw', 'Full data')