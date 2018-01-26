import urllib
import requests
import json
import pandas as pd
import logging
from pandas import ExcelWriter
from pandas.io.json import json_normalize
from Scripts.Get_File_Create_Modify_Time import last_modify_date
from Scripts.Get_Particular_Date import get_today_date
import xml.etree.ElementTree as ET

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')


def get_local_currency():

    currency_country = ['SGD', 'MYR', 'TWD', 'IDR', 'THB', 'CAD', 'EUR',
                        'GBP', 'JPY', 'MXN', 'PHP', 'CNY', 'USD', 'AUD']
    # currency_country = ['SGD', 'MYR']

    final_table_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
                       '-E·J- 2014.5.1\\2017.4.24 汇率\\local_currency.xlsx'

    currency_table = []
    run_check = None

    if last_modify_date(final_table_path) == get_today_date().strftime("%Y-%m-%d"):
        logging.info("Start to read today's currency table.")
        final_table = pd.read_excel(final_table_path)
    else:
        logging.info("Get today's currency table from currencyconverterapi.")
        while run_check is None:
            try:
                for country in currency_country:
                    request_url = 'https://free.currencyconverterapi.com/api/v5/convert?q=USD_' + country
                    res = requests.get(request_url)
                    result = res.text
                    parsed = json.loads(result)
                    # result = json.dumps(parsed, indent=4, sort_keys=True)
                    result = json.dumps(parsed)
                    # 去掉index
                    json_result = pd.read_json(result).reset_index()
                    # 去掉最后一行
                    json_result = json_result[:-1]

                    # json_result['results_edited'] = json_result['results'].apply(json.loads).apply(json_normalize)
                    # json_result = json_normalize(parsed, 'val', )
                    # print(pd.DataFrame(x['val'] for x in json_result['results']))

                    # 取字典里面的汇率
                    json_result['Currency'] = pd.DataFrame(str(x['val']) for x in json_result['results'])
                    json_result['Currency'] = float(json_result['Currency'])

                    currency_table.append(json_result)
                    logging.info(country + ' is added in to currency table.')

                run_check = 1
                final_table = pd.concat(currency_table)
                logging.info("Currency table is downloaded.")

                # 添加必要列
                final_table['currency_name_long'] = final_table['index'].str[4:]
                final_table['currency_name'] = final_table['currency_name_long'].str[:2]
                final_table['last update date'] = get_today_date()
                final_table['last update time'] = None

                final_table = final_table[['currency_name', 'Currency', 'last update date',
                                           'last update time', 'currency_name_long']]

                # 输出到excel
                writer = ExcelWriter(final_table_path)
                final_table.to_excel(writer, 'Sheet1')
                writer.save()
                logging.info("Currency table is exported to local_currency.xlsx")

            except Exception as err:
                logging.info('An exception happened: ' + str(err) + ', now try again.')

    return final_table


def get_local_currency_abandon():
    requestURL = 'http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.' \
                 'finance.xchange%20where%20pair%20in%20(%22USDSGD%22,%20%22USDMYR%22,%20%' \
                 '22USDTWD%22,%20%22USDIDR%22,%20%22USDTHB%22)&env=store://datatables.org/alltableswithkeys'
    try:
        xml_file = urllib.request.urlopen(requestURL)
        tree = ET.parse(xml_file)
        root = tree.getroot()

        # print(root)
        # print('\n')

        items = root.findall('results/rate')
        currency_list = pd.DataFrame(columns=('currency_name', 'Currency'))
        # print(currency_list)
        for item in items:
            currency_name_usd = item.find('Name').text
            currency_name = currency_name_usd.split('/')[1][:2]
            currency_num = float(item.find('Rate').text)

            # print(currency_name, currency_num)
            append_list = pd.DataFrame([[currency_name, currency_num]],
                                       columns=('currency_name', 'Currency'))
            # print(append_list)
            currency_list = currency_list.append(append_list, ignore_index=True)

    except Exception as err:
        print('An exception happened: ' + str(err) + ', and we cannot download currency list via Yahoo API.')
        print('Start download Yahoo currency list from csv.')

        try:
            currency_list = pd.read_csv(
                'http://download.finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&'
                's=USDSGD=X,USDMYR=X,USDTWD=X,USDIDR=X,USDTHB=X,USDCAD=X,USDEUR=X,'
                'USDGBP=X,USDJPY=X,USDMXN=X,USDPHP=X,USDCNY=X,USDUSD=X',
                header=-1)

            currency_list.columns = ['currency_name', 'Currency', 'last update date', 'last update time']
            currency_list['currency_name_long'] = currency_list['currency_name'].str[3:6]
            currency_list['currency_name'] = currency_list['currency_name'].str[3:5]

            # 下载一份到本地
            writer = ExcelWriter("D://Program Files (x86)//百度云同步盘//Dropbox//-E·J- 2014.5.1//2017.4.24 汇率//"
                                 "local_currency.xlsx")
            currency_list.to_excel(writer, 'Sheet1')
            writer.save()

        except Exception as err:
            print('An exception happened: ' + str(err) + ', and we cannot download currency list via Yahoo csv.')
            print('Start reading yesterday currency.')
            currency_list = pd.read_excel("D://Program Files (x86)//百度云同步盘//Dropbox//-E·J- 2014.5.1//2017.4.24 汇率//"
                                          "local_currency.xlsx")

    return currency_list


def get_local_currency_abandon_1():

    try:
        currency_list = pd.read_csv(
            'http://download.finance.yahoo.com/d/quotes.csv?e=.csv&f=sl1d1t1&'
            's=USDSGD=X,USDMYR=X,USDTWD=X,USDIDR=X,USDTHB=X,USDCAD=X,USDEUR=X,'
            'USDGBP=X,USDJPY=X,USDMXN=X,USDPHP=X,USDCNY=X,USDUSD=X',
            header=-1)

        currency_list.columns = ['currency_name', 'Currency', 'last update date', 'last update time']
        currency_list['currency_name_long'] = currency_list['currency_name'].str[3:6]
        currency_list['currency_name'] = currency_list['currency_name'].str[3:5]

        # 下载一份到本地
        writer = ExcelWriter("D://Program Files (x86)//百度云同步盘//Dropbox//-E·J- 2014.5.1//2017.4.24 汇率//"
                             "local_currency.xlsx")
        currency_list.to_excel(writer, 'Sheet1')
        writer.save()

    except Exception as err:
        print('An exception happened: ' + str(err) + ', and we cannot download currency list via Yahoo csv.')
        print('Start reading yesterday currency.')
        currency_list = pd.read_excel("D://Program Files (x86)//百度云同步盘//Dropbox//-E·J- 2014.5.1//2017.4.24 汇率//"
                                      "local_currency.xlsx")

    return currency_list


if __name__ == '__main__':
    print(get_local_currency())
