from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import re


def get_smt_search_result():
    html = urlopen('https://www.aliexpress.com/wholesale?'
                   'catId=0'
                   '&SearchText=universal+laptop+adapter')
    bsObj = BeautifulSoup(html.read(), 'lxml')
    # 查找所有的item
    itemList = bsObj.findAll('li', {'class': re.compile("list-item*")})
    # 要抓取的attribute
    to_scraped_attr = [['itemID', 'value', 'input', 'atc-product-id'],
                       ['shopName', 'title', 'a', 'store '],
                       ['shopURL', 'href', 'a', 'store '],
                       ['itemName', 'title', 'a', 'history-item product '],
                       ['itemURL', 'href', 'a', 'history-item product ']]

    # 要抓取的text
    to_scraped_text = [['sales_price', 'span', 'value'],
                       ['comment', 'a', 'rate-num '],
                       ['orders', 'a', 'order-num-a ']]

    # 创建一个空的data frame
    item_info_column = ['itemID',
                        'shopName',
                        'shopURL',
                        'itemName',
                        'itemURL',
                        'sales_price',
                        'comment',
                        'orders']

    item_info_list = pd.DataFrame(columns=item_info_column)

    # 把attribute加入到data frame中
    i = 0
    for item in itemList:
        # 提取存储在attribute里面的数据
        for column_name, value_position, tag_name, class_name in to_scraped_attr:
            item_attr = None
            item_attr = item.find(tag_name, {'class': class_name}).attrs[value_position]
            item_info_list.set_value(i, column_name, item_attr)

        # 提取储存在text里面的数据
        for column_name, tag_name, class_name in to_scraped_text:
            item_text = None
            try:
                item_text = item.find(tag_name, {'class': class_name}).get_text()
                item_info_list.set_value(i, column_name, item_text)
            except Exception as err:
                print('An exception happened: ' + str(err))

        i = i + 1

    # 修正data frame
    item_info_list['sales_price'] = item_info_list['sales_price'].str[4:]
    item_info_list['comment'] = item_info_list['comment'].str[1:].str[:-1]
    item_info_list['orders'] = item_info_list['orders'].str.split('(').str[1].str.split(')').str[0]

    # 输出data frame到csv
    item_info_list.to_csv('D:\\smt_item_list.csv', sep=',')

