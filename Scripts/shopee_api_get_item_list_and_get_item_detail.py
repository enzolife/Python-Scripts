
# coding: utf-8

# In[1]:

import requests
import time
import datetime
import pandas as pd

import hashlib
import hmac
import base64

import json

from pandas.io.json import json_normalize

import numpy
import logging


# In[2]:

# Current time stamp
timestamp = int(time.time())


# In[3]:

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')


# In[4]:

# logging.info('yes')


# In[5]:

# Date
today_date = datetime.date.today() + datetime.timedelta(days=0)
yesterday_date = datetime.date.today() + datetime.timedelta(days=-1)
seven_days_before_date = datetime.date.today() + datetime.timedelta(days=-7)


# In[6]:

today_date.strftime('%Y_%m_%d')


# In[7]:

# shop parameter list
# partner_id, shopid, shop_name, shop_key
shop_parameter_list = [   [12156, 25482220, 'tengus.tw', '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'],
   [14689, 53580963, 'qianjiaozi.my', '93815a723e386c9b91379a94f31538853582e02e085e180e0d52c841f7b53e19'],
   [12156, 59848325, 'tengus.my', '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'],
   [12156, 59846508, 'tengus.id', '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'],
   [16363, 58707738, 'qianjiaozi', 'ff53513499d845aa1a2fccc7d3731f43a6ce8939d0375a1cc4f31eb1cb916ea3'],
   [12156, 62417386, 'tengus1.id', '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'],
   [12156, 62417551, 'tengus2.id', '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'],
   [12156, 62416366, 'tengus1.tw', '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'],
   [12156, 62416544, 'tengus2.tw', '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'],
   [12156, 62418141, 'tengus1.my', '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'],
   [12156, 62418493, 'tengus2.my', '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'],
   [16363, 63534861, 'qianjiaozitw1', 'ff53513499d845aa1a2fccc7d3731f43a6ce8939d0375a1cc4f31eb1cb916ea3'],
   [17701, 62887142, 'yilanlu.tw', 'f3e23e0a873b0d74bb8a05b03a77e7a7a03bfebdba622d685b64aa926467d8b9'],
   [16363, 66377809, 'qianjiaozi1', 'ff53513499d845aa1a2fccc7d3731f43a6ce8939d0375a1cc4f31eb1cb916ea3']
  ]

columns = ['partner_id', 'shopid', 'shop_name', 'shop_key']
shop_parameter_df = pd.DataFrame(shop_parameter_list, columns=columns)
# shop_parameter_df


# In[8]:

# get_auth_signature
def get_auth_signature(url, payload, shop_key):
    # API Key
    shopee_secret = shop_key
    # Post Message
    post_message = url + '|' + json.dumps(payload)
    # HMAC-SHA256
    message = bytes(post_message, 'utf-8')
    secret = bytes(shopee_secret, 'utf-8')
    hash = hmac.new(secret, message, hashlib.sha256)
    auth_signature = hash.hexdigest()
    return auth_signature


# In[9]:

# URL
url = 'https://partner.shopeemobile.com/api/v1/items/get'


# In[10]:

# get all item for each shop & get item_detail for each item
for key, shop in shop_parameter_df.iterrows():
    all_item_list = pd.DataFrame()
    # parameter
    partner_id = shop['partner_id']
    shopid = shop['shopid']
    shop_key = shop['shop_key']
    shop_name = shop['shop_name']
    timestamp = int(time.time())
    
    # get all item
    logging.info('Retrieving item from ' + shop_name + '.')
    max_page = 200
    pagination_entries_per_page = 100
    i = 0

    try:
        while i <= max_page:
            # start entry
            start_entry = i * pagination_entries_per_page

            # Parameter
            pagination_offset = start_entry

            # payload
            payload = {"partner_id":partner_id,
                       "shopid":shopid,
                       "timestamp":timestamp,
                       "pagination_offset":pagination_offset,
                       "pagination_entries_per_page":pagination_entries_per_page}
            # Auth Signature
            Auth_signature = get_auth_signature(url, payload, shop_key)
            # HTML Header
            headers = {"Host": "partner.shopeemobile.com",
                        "Content-Type": "application/json",
                        "Content-Length": "89",
                        "Authorization": Auth_signature}
            # HTML Body
            payload = json.dumps(payload)
            # Post Request
            r = requests.post(url, data=payload, headers=headers)
            # 打印原始Json
            parsed = json.loads(r.text)
            # 漂亮打印Json
            item_list = json_normalize(parsed['items'])
            # 排除update_time
            selected_column = ['item_id', 'shopid', 'status']
            item_list = item_list[selected_column]

            # 合并
            if i == 0:
                all_item_list = item_list
            else:
                all_item_list = all_item_list.append(item_list)
            i += 1
            logging.info('Retrieving item from page ' + str(i))
    except:
        pass

    # 判断item_list是否非空
    if all_item_list.empty:
        logging.info('No item in shopid:' + str(shopid) + '.')
    else:
        # 去重
        logging.info('Remove duplicate records.')
        all_item_list = all_item_list.drop_duplicates('item_id').reset_index()
        logging.info('Retrieved item list.')
        
        # get item detail
        item_detail_url = 'https://partner.shopeemobile.com/api/v1/item/get'
        
        item_detail_list = pd.DataFrame()
        
        for key, item in all_item_list.iterrows():
            try:
                item_id = item['item_id']
                logging.info('Now retrieving itemid: ' + str(item_id) + ' detail.')
                # payload
                payload = {"partner_id":partner_id,
                           "shopid":shopid,
                           "timestamp":timestamp,
                           "item_id": item_id}
                # Auth Signature
                Auth_signature = get_auth_signature(item_detail_url, payload, shop_key)
                # HTML Header
                headers = {"Host": "partner.shopeemobile.com",
                            "Content-Type": "application/json",
                            "Content-Length": "89",
                            "Authorization": Auth_signature}
                # HTML Body
                payload = json.dumps(payload)
                # Post Request
                r = requests.post(item_detail_url, data=payload, headers=headers)
                # 打印原始Json
                parsed = json.loads(r.text)
                # 提取item部分
                item_detail = json_normalize(parsed['item'])
                # 只提取所需columns
                item_detail_columns = ['item_id', 'item_sku', 'likes', 'name', 'create_time', 'update_time', 'original_price', 'price', 'sales', 'shopid', 'status', 'stock', 'views', 'currency']
                item_detail = item_detail[item_detail_columns]
                # 替换column names
                replace_columns_name = {
                    'item_id': '产品ID',
                    'item_sku': '商品SKU',
                    'likes': '点赞数',
                    'name': '产品名',
                    'create_time': '创建时间',
                    'update_time': '最后更新时间',
                    'original_price': '原价',
                    'price': '现价',
                    'sales': '销量',
                    'shopid': '店铺ID',
                    'status': '产品状态',
                    'stock': '库存', 
                    'views': '点击量',
                    'currency': '货币'
                }
                item_detail = item_detail.rename(columns=replace_columns_name)
                # column重新排序
                sort_columns = [
                    '产品ID',
                    '店铺ID',
                    '商品SKU',
                    '产品状态',
                    '产品名',
                    '货币',
                    '创建时间',
                    '最后更新时间',
                    '原价',
                    '现价',
                    '点赞数',
                    '点击量',
                    '销量',
                    '库存'
                ]
                item_detail = item_detail[sort_columns]
                
                # 添加到总表
                item_detail_list = item_detail_list.append(item_detail)
                # print(item_detail)
                logging.info('Retrieved ' + str(item_id) + ' detail.')
            except:
                logging.info('Retrieve ' + str(item_id) + ' not successfully.')
                pass

        # 添加记录时间
        item_detail_list['记录时间'] = today_date
        # 修改create / update time的格式
        item_detail_list['创建时间'] = pd.to_datetime(item_detail_list['创建时间'], unit='s').dt.date
        item_detail_list['最后更新时间'] = pd.to_datetime(item_detail_list['最后更新时间'], unit='s').dt.date
        # 添加销量/点击量
        item_detail_list['销量/点击量'] = item_detail_list['销量']/item_detail_list['点击量']
        # 添加销量/点赞数
        item_detail_list['销量/点赞数'] = item_detail_list['销量']/item_detail_list['点赞数']
        # 产品是否在折扣中
        item_detail_list['促销中？'] = item_detail_list['原价'] != item_detail_list['现价']            
        # 按销量排序
        item_detail_list = item_detail_list.sort_values(by=['销量'], ascending=False)
        
        # export to yifang cloud
        export_folder = 'D://Program Files (x86)//FangCloudV2//寶寶優選//寶寶優選公共资料库//10 【数据】//'
        item_detail_list.to_csv(export_folder + "item_detail_list_ " + str(shopid)+ "_" + today_date.strftime('%Y_%m_%d') + ".csv", sep=',')

logging.info('Finished.')

