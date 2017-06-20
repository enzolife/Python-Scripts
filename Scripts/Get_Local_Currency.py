import urllib
import requests
import pandas as pd
import xml.etree.ElementTree as ET


def get_local_currency():
    requestURL = 'http://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.' \
                 'finance.xchange%20where%20pair%20in%20(%22USDSGD%22,%20%22USDMYR%22,%20%' \
                 '22USDTWD%22,%20%22USDIDR%22,%20%22USDTHB%22)&env=store://datatables.org/alltableswithkeys'

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
        currency_num = item.find('Rate').text

        # print(currency_name, currency_num)
        append_list = pd.DataFrame([[currency_name, currency_num]],
                                   columns=('currency_name', 'Currency'))
        # print(append_list)
        currency_list = currency_list.append(append_list, ignore_index=True)

    return currency_list
