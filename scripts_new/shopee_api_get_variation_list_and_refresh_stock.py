
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

from pprint import pprint 

from pandas.io.json import json_normalize

import numpy


# In[2]:

# Current time stamp
timestamp = int(time.time())


# In[3]:

# Date
today_date = datetime.date.today() + datetime.timedelta(days=0)
yesterday_date = datetime.date.today() + datetime.timedelta(days=-1)
seven_days_before_date = datetime.date.today() + datetime.timedelta(days=-7)


# In[4]:

# Shop Parameter；tengus.tw
partner_id = 12156
shopid = 25482220
shop_key = '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'

# Shop Parameter；qianjiaozi.my
partner_id = 14689
shopid = 53580963
shop_key = '93815a723e386c9b91379a94f31538853582e02e085e180e0d52c841f7b53e19'

# Shop Parameter；tengus.id
partner_id = 12156
shopid = 59846508
shop_key = '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'


# In[5]:

# get_auth_signature
def get_auth_signature(url, payload):
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


# In[6]:

# get item list URL
url = 'https://partner.shopeemobile.com/api/v1/items/get'


# In[7]:

# get all item
max_page = 20
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
        Auth_signature = get_auth_signature(url, payload)
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
        print('now i is ' + str(i))
except:
    pass

# 去重
all_item_list = all_item_list.drop_duplicates('item_id').reset_index()
print("There are " + str(len(all_item_list)) + " items in this shop.")


# In[8]:

# update variation stock url
update_variation_stock_url = 'https://partner.shopeemobile.com/api/v1/items/update_variation_stock'


# In[ ]:

# 正式批量修改variation
# 有限循环，避免更新不完整跳出，更新100次
i = 1
while True:
    if i % 2==0:
        stock_add = 1
    else:
        stock_add = -1
    
    if i == 100:
        break
    
    print("Now run the " + str(i) + " time.")

    for item_id in item_list['item_id']:
        # Get Item Detail URL
        get_item_detail_url = 'https://partner.shopeemobile.com/api/v1/item/get'
        # Current time stamp
        timestamp = int(time.time())
        # payload
        payload = {"partner_id":partner_id,
                   "shopid":shopid,
                   "timestamp":timestamp,
                   "item_id":int(item_id)}
        # Auth Signature
        Auth_signature = get_auth_signature(get_item_detail_url, payload)
        # HTML Header
        headers = {"Host": "partner.shopeemobile.com",
                    "Content-Type": "application/json",
                    "Content-Length": "89",
                    "Authorization": Auth_signature}
        # HTML Body
        payload = json.dumps(payload)
        # Post Request
        r = requests.post(get_item_detail_url, data=payload, headers=headers)
        # 打印原始Json
        parsed = json.loads(r.text)
        result = json.dumps(parsed, indent=4, sort_keys=True)
        # Try是否有Varation，如果没有就跳过
        try:
            # 列出variation
            item_data_frame = json_normalize(parsed['item'])
            item_data_frame = item_data_frame[['item_id', 'variations']]
            # variation to json，列出item_id
            item_data_frame_json = item_data_frame.to_json(orient='records')
            # final variation data frame，列出含item_id的variation列表
            final_item_data_frame = json_normalize(json.loads(item_data_frame_json),record_path='variations',meta=['item_id'])

            # update variation stock url
            update_variation_stock_url = 'https://partner.shopeemobile.com/api/v1/items/update_variation_stock'

            # 找出每一个variation id，进行update variation stock
            for variation_id, variation_stock in zip(final_item_data_frame['variation_id'], final_item_data_frame['stock']):
                # Current time stamp
                timestamp = int(time.time())

                # 判断原有stock的大小，如果小于5的话，直接更改为10
                if int(variation_stock) < 5:
                    variation_stock = 10

                # payload
                payload = {"partner_id":partner_id,
                           "shopid":shopid,
                           "timestamp":timestamp,
                           "item_id":int(item_id),
                           "variation_id":int(variation_id),
                           "stock":int(variation_stock) + stock_add}
                # Auth Signature
                Auth_signature = get_auth_signature(update_variation_stock_url, payload)
                # HTML Header
                headers = {"Host": "partner.shopeemobile.com",
                            "Content-Type": "application/json",
                            "Content-Length": "89",
                            "Authorization": Auth_signature}
                # HTML Body
                payload = json.dumps(payload)
                # Post Request
                r = requests.post(update_variation_stock_url, data=payload, headers=headers)
                print(r.text)
                # Notice
                print(str(item_id) + ', ' + str(variation_id) + ' stock updated to ' + str(int(variation_stock) + stock_add))
                time.sleep(30)
        except Exception as err:
            print('An exception occured: ' + str(err))
            
    i = i + 1

