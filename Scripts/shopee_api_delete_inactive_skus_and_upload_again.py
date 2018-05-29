
# coding: utf-8

# In[58]:

import requests
import time
import datetime as dt
import pandas as pd

import hashlib
import hmac
import base64

import json

from pprint import pprint 

from pandas.io.json import json_normalize

import numpy
import logging


# In[59]:

logging.basicConfig(level=logging.INFO, 
                    format=' %(asctime)s - %(levelname)s - %(message)s')


# In[60]:

# Date
today_date = dt.date.today() + dt.timedelta(days=0)
yesterday_date = dt.date.today() + dt.timedelta(days=-1)
seven_days_before_date = dt.date.today() + dt.timedelta(days=-7)


# In[61]:

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


# In[62]:

def post_message_to_shopee_api(url, payload, shop_key):
    # Auth Signature
    auth_signature = get_auth_signature(url, payload, shop_key) 
    # HTML Header
    headers = {"Host": "partner.shopeemobile.com",
                "Content-Type": "application/json",
                "Content-Length": "89",
                "Authorization": auth_signature}
    # HTML Body
    payload = json.dumps(payload)
    # Post Request
    r = requests.post(url, data=payload, headers=headers)
    # 打印原始Json
    parsed = json.loads(r.text)
    return parsed


# In[63]:

# get_item_list
def get_item_list(partner_id, shopid, shop_key):
    # parameters
    max_page = 200
    pagination_entries_per_page = 100
    i = 0
    # Current time stamp
    timestamp = int(time.time())
    # URL
    url = 'https://partner.shopeemobile.com/api/v1/items/get'
    
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
            # post_message_to_shopee_api
            parsed = post_message_to_shopee_api(url, payload, shop_key)
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

    # 去重
    logging.info('Remove duplicate records.')
    all_item_list = all_item_list.drop_duplicates('item_id').reset_index()
    logging.info('Retrieved item list.')
    return all_item_list


# In[64]:

# get_item_detail
def get_item_detail(partner_id, shopid, shop_key, all_item_list):
    # empty item_detail_list
    item_detail_list = pd.DataFrame()
    # Current time stamp
    timestamp = int(time.time())
    # get item detail
    url = 'https://partner.shopeemobile.com/api/v1/item/get'
    
    for key, item in all_item_list.iterrows():
        try:
            item_id = item['item_id']
            logging.info('Now retrieving ' + str(item_id) + ' detail.')
            # payload
            payload = {"partner_id":partner_id,
                       "shopid":shopid,
                       "timestamp":timestamp,
                       "item_id": item_id}
            # post_message_to_shopee_api
            parsed = post_message_to_shopee_api(url, payload, shop_key)
            # 漂亮打印Json
            item_detail = json_normalize(parsed['item'])
            item_detail_list = item_detail_list.append(item_detail)
            logging.info('Retrieved ' + str(item_id) + ' detail.')
        except:
            pass

    # convert timestamp to date
    item_detail_list['create_time'] = pd.to_datetime(item_detail_list['create_time'], unit='s').dt.date
    item_detail_list['update_time'] = pd.to_datetime(item_detail_list['update_time'], unit='s').dt.date
    item_detail_list['days_since_live'] = (today_date - item_detail_list['create_time']).dt.days

    return item_detail_list


# In[65]:

# retrieve_dict_and_convert_to_df_column
def retrieve_dict_and_convert_to_df_column(dataframe, column_name, selected_key_list, converted_column_name):

    edited_column_list = []

    for index, record in dataframe.iterrows():
        to_edit_column = pd.DataFrame(record[column_name])
        try:
            to_edit_column = to_edit_column[selected_key_list]
            to_edit_column_dict = to_edit_column.to_dict('records')
        except:
            to_edit_column_dict = '[]'
        edited_column_list.append(to_edit_column_dict)
    
    dataframe[converted_column_name] = edited_column_list
    return dataframe


# In[66]:

# retrieve_image_and_convert_to_dict
def retrieve_image_and_convert_to_dict(dataframe, column_name, converted_column_name):
    edited_column_list = []
    for index, record in dataframe.iterrows():
        img_url_dict_list = []
        to_edit_column = pd.DataFrame(record[column_name])
        for index, img_url in to_edit_column.iterrows():
            img_url_dict = {'url': img_url[0]}
            img_url_dict_list.append(img_url_dict)
        edited_column_list.append(img_url_dict_list)
    dataframe[converted_column_name] = edited_column_list
    return dataframe


# In[67]:

# 根据每个分类，找到必填的attributes，然后填上
def get_category_attributes(partner_id, shopid, shop_key, category_id):
    # Current time stamp
    timestamp = int(time.time())
    
    payload = {"partner_id":partner_id,
               "shopid": shopid,
               "timestamp": timestamp,
               "category_id": category_id}

    url = 'https://partner.shopeemobile.com/api/v1/item/attributes/get'

    # post_message_to_shopee_api
    parsed = post_message_to_shopee_api(url, payload, shop_key)
    # 漂亮打印Json
    attribute_list = json_normalize(parsed['attributes'])
    attribute_list['category_id'] = category_id
    
    # 查找是否有error
    
    return attribute_list


# In[68]:

# 找店铺分类
def get_category_info(partner_id, shopid, shop_key):
    
    # Current time stamp
    timestamp = int(time.time())
    
    payload = {"partner_id":partner_id,
               "shopid": shopid,
               "timestamp": timestamp}

    url = 'https://partner.shopeemobile.com/api/v1/item/categories/get'

    # post_message_to_shopee_api
    parsed = post_message_to_shopee_api(url, payload, shop_key)
    # 漂亮打印Json
    category_list = json_normalize(parsed['categories'])
    
    # 查找是否有error
    
    return category_list


# In[69]:

# 删除产品
def delete_product(partner_id, shopid, shop_key, delete_product_id):
    # Current time stamp
    timestamp = int(time.time())
    
    # payload
    payload = {
               "item_id": delete_product_id,
               "partner_id": partner_id,
               "shopid": shopid,
               "timestamp": timestamp
               }

    # print(payload)
    
    url = 'https://partner.shopeemobile.com/api/v1/item/delete'

    # post_message_to_shopee_api
    parsed = post_message_to_shopee_api(url, payload, shop_key)
    logging.info('Product ID: ' + str(delete_product_id) + ' is deleted.')
    
    # 查找是否有error


# In[70]:

# 添加商品图片
def add_product_image(partner_id, shopid, shop_key, item_id, images):
    # 上传中可能失败；尝试到找不到fail_image为止
    while len(images) != 0:
        # Current time stamp
        timestamp = int(time.time())

        # payload
        payload = {
                    "item_id": item_id,
                    "images": images,
                    "partner_id": partner_id,
                    "shopid": shopid,
                    "timestamp": timestamp
                   }

        url = 'https://partner.shopeemobile.com/api/v1/item/img/add'

        # post_message_to_shopee_api
        parsed = post_message_to_shopee_api(url, payload, shop_key)
        # print(parsed)
        logging.info('add_product_image - Images for Product ID: ' + str(item_id) + ' are added.')
        # 清空images
        images = []
        
        # 查找是否有error

        # 查找是否有上传失败的图片
        if 'fail_image' in parsed.keys():
            logging.info('add_product_image - Start to upload failed images.')
            images = parsed['fail_image']


# In[71]:

# 添加商品图片到某个指定位置
def add_product_image_to_certain_location(partner_id, shopid, shop_key, item_id, image_url, image_position):
    # 上传中可能失败；尝试到找不到fail_image为止
    while len(image_url) != 0:
        # Current time stamp
        timestamp = int(time.time())

        # payload
        payload = {
                    "item_id": item_id,
                    "image_url": image_url,
                    "image_position": image_position,
                    "partner_id": partner_id,
                    "shopid": shopid,
                    "timestamp": timestamp
                   }

        url = 'https://partner.shopeemobile.com/api/v1/item/img/insert'

        # post_message_to_shopee_api
        parsed = post_message_to_shopee_api(url, payload, shop_key)
        logging.info(parsed)
        # 查找是否有上传失败的图片
        if 'error' in parsed.keys():
            logging.warning('add_product_image - Error occurred. Upload agaign')
        else:
            logging.info('add_product_image_to_certain_location - Images for Product ID: ' + str(item_id) + ' are added.')
            # 清空images
            image_url = ''


# In[72]:

# 新增产品
def add_product(partner_id, shopid, shop_key,
                category_id,
                name,
                description,
                price,
                stock,
                item_sku,
                edited_variations,
                edited_images,
                edited_attributes,
                edited_logistics,
                weight
               ):
    # Current time stamp
    timestamp = int(time.time())
    
    # payload
    payload = {
                "category_id": category_id,
                "name": name,
                "description": description,
                "price": price,
                "stock": stock,
                "item_sku": item_sku,
                "images": edited_images,
                "weight": weight,
                "logistics": edited_logistics,
                # "days_to_ship": days_to_ship,
                "partner_id": partner_id,
                "shopid": shopid,
                "timestamp": timestamp
               }
    
    # 判断条件是否为空
    if edited_variations != '[]':
        payload['variations'] = edited_variations
        
    if edited_attributes != '[]':
        payload['attributes'] = edited_attributes
        
    # print(payload)

    url = 'https://partner.shopeemobile.com/api/v1/item/add'

    # post_message_to_shopee_api
    logging.info('add_product - Add Product SKU: ' + str(item_sku))
    parsed = post_message_to_shopee_api(url, payload, shop_key)
    # print(parsed)
    
    # 查找是否有error
    if 'error' in parsed.keys():
        logging.warning(parsed)
        return False
    else:
        item_id = parsed['item_id']
        # 查找是否有failed images
        if 'fail_image' in parsed.keys():
            # 判断是否有图片上传失败；如果失败要重传
            try:
                fail_image_list = parsed['fail_image']
                # print(fail_image_list)
                logging.info('add_product - Try to upload failed images.')
                for fail_image in fail_image_list:
                    # 查找在原来的image list里面，它是在哪个位置；要把它放回到原来的位置上
                    logging.info('add_product - Now upload failed image: ' + str(fail_image))
                    fail_image_position = 0
                    for index, value in enumerate(edited_images):
                        original_image_url = value['url']
                        logging.info('Original images: ' + str(original_image_url))
                        if original_image_url == fail_image:
                            fail_image_position = index + 1
                            logging.info('add_product - Failed images ' + str(fail_image) + ' is at location ' + str(fail_image_position))
                    logging.info('add_product - Upload image to position: ' + str(fail_image_position))
                    add_product_image_to_certain_location(partner_id, shopid, shop_key, item_id, fail_image, fail_image_position)        
                    # add_product_image(partner_id, shopid, shop_key, item_id, fail_image_list)
                logging.info('add_product - Images are added.')
            except Exception as err:
                logging.info('add_product - An exception occurred: ' + str(err))
        logging.info('add_product - Product ID: ' + str(item_id) + ' is added.')
        return True


# In[73]:

# shop parameter list# shop  
# partner_id, shopid, shop_name, shop_key
shop_parameter_list = [   [12155, 23070969, 'poweradapter.tw', 'de5e924b8ed680bc9b22a6c402058154340333ff05641a38069f2856a2f3e24e'],
   [12156, 25482220, 'tengus.tw', '60dbb2b5bcd937be4d6101cf70677908da72f4988c533d0c07b997fd22acd4f2'],
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


# In[74]:

def delect_inactive_skus_and_upload_again(partner_id, shopid, shop_name, shop_key):
    # 1. get item list
    all_item_list = get_item_list(partner_id, shopid, shop_key)
    # 2. get item detail list
    item_detail_list = get_item_detail(partner_id, shopid, shop_key, all_item_list)
    # 3. filter item detail list
    # 选上线超过60天仍然0销量的产品
    item_detail_list = item_detail_list[item_detail_list['days_since_live'] >= 60]
    item_detail_list = item_detail_list[item_detail_list['sales'] == 0]
    item_detail_list = item_detail_list.sort_values(by='days_since_live', ascending=False)
    # 如果不存在这样的list，直接跳过
    if len(item_detail_list) != 0:
        # 4. get item attributes list
        column_name = 'attributes'
        selected_key_list = ['attribute_id', 'attribute_value']
        converted_column_name = 'edited attributes'
        retrieve_dict_and_convert_to_df_column(item_detail_list, column_name, selected_key_list, converted_column_name)
        # 5. 把attribute_id改为attributes_id
        for value in item_detail_list['edited attributes']:
            for dict_value in value:
                dict_value['attributes_id'] = dict_value.pop('attribute_id')
                dict_value['value'] = dict_value.pop('attribute_value')
        # 6. 看店铺所有分类的必填attributes
        category_id_list = item_detail_list['category_id'].drop_duplicates()
        # 7. 获取这个店铺所有分类的attributes list
        attribute_full_list = pd.DataFrame()
        for category_id in category_id_list:
            # print(int(category_id))
            category_id = int(category_id)
            category_attribute = get_category_attributes(partner_id, shopid, shop_key, category_id)
            attribute_full_list = attribute_full_list.append(category_attribute)
        # 8. 给每个必填attribute提供default value
        attribute_default_value_list = [
            [5794, 9547, '握力'],
            [11460, 9547, '握力']
        ]
        attribute_default_value_columns = ['category_id', 'attribute_id', 'value']
        attribute_default_value_df = pd.DataFrame(attribute_default_value_list, columns=attribute_default_value_columns)
        attribute_full_list = pd.merge(attribute_full_list, attribute_default_value_df, how='left',
                                   left_on=['category_id', 'attribute_id'], right_on=['category_id', 'attribute_id'])
        # 9. 检查每个产品的attributes
        # 检查现有的attributes是否在表里；如果不存在，要删除
        # 如果缺了必填的attributes，要补充回来
        for index, value in item_detail_list.iterrows():
            # 拿到每个产品的cat id
            category_id = value['category_id']
            # 创建一个空list，装这个产品的所有现有attributes
            existing_attribute = []

            # for loop所有这个产品的attributes，放在existing_attribute
            for dict_value in value['edited attributes']:
                existing_attribute.append(dict_value['attributes_id'])
            # print(existing_attribute)

            # 把这个cat的必填attribute拉出来
            cat_mandatory_attribute_df = (attribute_full_list[(attribute_full_list['category_id'] == category_id)
                                                               & (attribute_full_list['is_mandatory'] == True)])
            # print((cat_mandatory_attribute_list))

            # 把这个cat的非必填attribute拉出来
            cat_optional_attribute_df = (attribute_full_list[(attribute_full_list['category_id'] == category_id)
                                                               & (attribute_full_list['is_mandatory'] == False)])
            # print((cat_optional_attribute_list))

            # 判断必填attributes是不是在现有attributes内
            for index, attr in cat_mandatory_attribute_df.iterrows():
                mandatory_attribute_id = attr['attribute_id']
                mandatory_attribute_value = attr['value']

                if mandatory_attribute_id not in existing_attribute:
                    # print('attr: ' + str(mandatory_attribute_id) + ' is not in mandatory_attribute_list.')
                    attr_dict = {'attributes_id': mandatory_attribute_id,
                                 'value': mandatory_attribute_value}
                    value['edited attributes'].append(attr_dict)

            # 判断现有非必填attributes内是否有不符合的非必填attributes
            for attr in existing_attribute:
                # print(attr)
                if attr not in list(cat_mandatory_attribute_df['attribute_id']):
                    if attr not in list(cat_optional_attribute_df['attribute_id']):
                        print('attr: ' + str(attr) + ' is not in optional_attribute_list.')
                        # 删除这个不符合的非必填项
                        for dict_value in value['edited attributes']:
                            if dict_value['attributes_id'] == attr:
                                del dict_value

        # 10. 删减variations的内容
        column_name = 'variations'
        selected_key_list = ['name', 'stock', 'price', 'variation_sku']
        converted_column_name = 'edited variations'
        retrieve_dict_and_convert_to_df_column(item_detail_list, column_name, selected_key_list, converted_column_name)                 
        # 11. 删减logistics的内容
        column_name = 'logistics'
        selected_key_list = ['logistic_id', 'enabled']
        converted_column_name = 'edited logistics'
        retrieve_dict_and_convert_to_df_column(item_detail_list, column_name, selected_key_list, converted_column_name)
        # 12. 转换images的内容
        column_name = 'images'
        converted_column_name = 'edited images'
        retrieve_image_and_convert_to_dict(item_detail_list, column_name, converted_column_name)
        # 13. 选择需要提交的内容
        selected_columns = ["category_id","name","description","price","stock","item_sku","edited variations","images","edited attributes","edited logistics","weight","days_to_ship", 'item_id', 'edited images']
        edited_item_detail_list = item_detail_list[selected_columns]    
        # 测试
        test_item_detail_list = edited_item_detail_list[:5]
        test_item_detail_list    
        # 14. 先删除产品，再新增产品
        for index, item in test_item_detail_list.iterrows():
            category_id = item[0]
            name = item[1]
            description = item[2]
            price = item[3]
            stock = item[4]
            item_sku = item[5]
            edited_variations = item[6]
            images = item[7]
            edited_attributes = item[8]
            edited_logistics = item[9]
            weight = item[10]
            # days_to_ship = 3
            product_id = item[12]
            edited_images = item[13]

            # print(images)



            # add product
            add_product_success = add_product(partner_id, shopid, shop_key,
                                               category_id,
                                               name,
                                               description,
                                               price,
                                               stock,
                                               item_sku,
                                               edited_variations,
                                               edited_images,
                                               edited_attributes,
                                               edited_logistics,
                                               weight
                                               )    
            if add_product_success == True:
                # delete product
                delete_product(partner_id, shopid, shop_key, product_id)
    else:
        logging.warning('add_product - Theres are not products under this filter for ' + str(shop_name))


# In[75]:

def get_attribute_category_list(partner_id, shopid, shop_name, shop_key):
    # 1. get item list
    all_item_list = get_item_list(partner_id, shopid, shop_key)
    # 2. get item detail list
    item_detail_list = get_item_detail(partner_id, shopid, shop_key, all_item_list)
    item_detail_list.to_csv('D://item_detail_list.csv', sep=',')
    # 3. filter item detail list
    # 如果不存在这样的list，直接跳过
    if len(item_detail_list) != 0:
        # 6. 看店铺所有分类的必填attributes
        category_id_list = item_detail_list['category_id'].drop_duplicates()
        # 7. 获取这个店铺所有分类的attributes list
        attribute_full_list = pd.DataFrame()
        for category_id in category_id_list:
            # print(int(category_id))
            category_id = int(category_id)
            category_attribute = get_category_attributes(partner_id, shopid, shop_key, category_id)
            attribute_full_list = attribute_full_list.append(category_attribute)
    return attribute_full_list


# In[76]:

# 执行
attribute_list_for_all_shop = pd.DataFrame()

for index, shop_parameter in shop_parameter_df.iterrows():
    partner_id = shop_parameter[0]
    shopid = shop_parameter[1]
    shop_name = shop_parameter[2]
    shop_key = shop_parameter[3]
    
    if (shopid == 59846508) or (shopid == 23070969):
        delect_inactive_skus_and_upload_again(partner_id, shopid, shop_name, shop_key)
        # images = ['https://t12.baidu.com/it/u=2105759597,3540269422&fm=173&app=25&f=JPEG?w=500&h=518&s=3DBB6A96EA533CCC3E6F59A20300E009','https://t12.baidu.com/it/u=667913453,121168607&fm=173&app=25&f=JPEG?w=500&h=309&s=B582EBB47E1B2CC042B2D9A20300E008']
        # item_id = 1196145106
        # image_url = 'https://t12.baidu.com/it/u=2105759597,3540269422&fm=173&app=25&f=JPEG?w=500&h=518&s=3DBB6A96EA533CCC3E6F59A20300E009'
        # image_position = 2
        # add_product_image(partner_id, shopid, shop_key, item_id, images)
        # add_product_image_to_certain_location(partner_id, shopid, shop_key, item_id, image_url, image_position)
 
    # try:
        # 查找所有店铺的attribute list
        # attribute_list = get_attribute_category_list(partner_id, shopid, shop_name, shop_key)
        # attribute_list_for_all_shop = attribute_list_for_all_shop.append(attribute_list)
    # except:
        # pass
    
# attribute_list_for_all_shop

