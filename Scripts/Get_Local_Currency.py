import urllib
import requests
import pandas as pd
from pandas import ExcelWriter
import xml.etree.ElementTree as ET


def get_local_currency():

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


if __name__ == '__main__':
    print(get_local_currency())
