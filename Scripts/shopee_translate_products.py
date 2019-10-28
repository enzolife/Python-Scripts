
# coding: utf-8

# In[12]:

import pandas as pd
import os
import time
import logging
from datetime import date


# In[13]:

# 获取脚本的当前路径，避免计划执行时路径出错
home_dir = os.path.dirname(os.path.realpath(__file__))
# 更换workding directory
working_directory = home_dir
os.chdir(working_directory)


# In[14]:

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')


# In[15]:

folder_path = '../shopee_product_translation/'
tw_site_product_list = pd.read_excel(os.path.join(folder_path, 'tengus_tw_product_list.xlsx'))
# tw_site_product_list = pd.read_excel(os.path.join(folder_path, 'translated_product_2019_10_19.xlsx'))
# tw_site_product_list = tw_site_product_list[tw_site_product_list['是否翻译'] == 'no']
# tw_site_product_list.head(5)


# In[16]:

# tw_site_product_list.columns


# In[17]:

# tw_site_product_list = tw_site_product_list[tw_site_product_list['产品id'] == 2496637042]


# In[18]:

# top_cat_in_tw = tw_site_product_list[['分类ID', '产品id']].groupby('分类ID').agg({'产品id': 'nunique'}).reset_index().sort_values(by='产品id', ascending=False).reset_index().head(5)
# top_cat_in_tw


# In[19]:

# top_cat_id = top_cat_in_tw['分类ID'][0]
# top_cat_id


# In[20]:

output_excel_columns = [
                        '变种名称',
                        '变种属性名称一',
                        '变种属性名称二',
                        '变种属性值一',
                        '变种属性值二',
                        '*价格（必填）',
                        '*库存（必填）',
                        '*重量(kg)(必填）',
                        '*主图（URL）地址（必填）',
                        '附图1',
                        '附图2',
                        '附图3',
                        '附图4',
                        '附图5',
                        '附图6',
                        '附图7',
                        '附图8',
                        '变种图',
                        '长(cm)',
                        '宽(cm)',
                        '高(cm)',
                        '发货期',
                        '来源URL',
                        '尺码图'
]


# In[21]:

tw_site_product_list_selected_columns = ['分类ID', '产品属性', 'Parent SKU', '产品标题', '产品描述', 'sku', '变种名称', '变种属性名称一',
       '变种属性名称二', '变种属性值一', '变种属性值二', '价格', '库存', '重量', '主图（URL）地址', '附图1',
       '附图2', '附图3', '附图4', '附图5', '附图6', '附图7', '附图8地址', '变种图', '长（cm）',
       '宽（cm）', '高（cm）', '发货期', '来源URL', '尺码图']


# In[22]:

tw_site_product_list_with_selected_columns = tw_site_product_list[tw_site_product_list_selected_columns]
# tw_site_product_list_with_selected_columns.head(5)


# In[23]:

# tw_site_product_list_with_selected_columns = tw_site_product_list_with_selected_columns[tw_site_product_list_with_selected_columns['分类ID'] == top_cat_id].reset_index()
# tw_site_product_list_with_selected_columns


# In[24]:

# 把1688的来源url拆出来，把productid填充为parent sku
tw_site_product_list_with_selected_columns['Parent SKU'] = tw_site_product_list_with_selected_columns['来源URL'].str.split("/", n = 4, expand = True)[4].str.split(".", n = 1, expand=True)[0]
# tw_site_product_list_with_selected_columns.head(5)


# In[25]:

# remove emoji
import re

emoji_pattern = re.compile(
                u'['
                u'\U0001F300-\U0001F64F'
                u'\U0001F680-\U0001F6FF'
                u'\u2600-\u2B55'
                u'\u23cf'
                u'\u23e9'
                u'\u231a'
                u'\u3030'
                u'\ufe0f'
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u'\U00010000-\U0010ffff'
                u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
                u'\U00002702-\U000027B0]+', flags=re.UNICODE)

def remove_emoji(text):
    return emoji_pattern.sub(r'', text)

# remove_emoji('ins爆款 🥕胡蘿卜🥕寶寶針織竹節棉爬服 嬰兒兔裝 嬰兒連身衣 寶寶包屁衣連身衣 中間開襟包屁衣 寶寶連體衣哈衣爬服')


# In[26]:

tw_site_product_list_with_selected_columns['产品标题'] = [remove_emoji(x) for x in tw_site_product_list_with_selected_columns['产品标题']]
tw_site_product_list_with_selected_columns['产品描述'] = [remove_emoji(x) for x in tw_site_product_list_with_selected_columns['产品描述']]


# In[27]:

tw_site_product_list_with_selected_columns['长（cm）'] = tw_site_product_list_with_selected_columns['长（cm）'].fillna(18)
tw_site_product_list_with_selected_columns['宽（cm）'] = tw_site_product_list_with_selected_columns['宽（cm）'].fillna(13)
tw_site_product_list_with_selected_columns['高（cm）'] = tw_site_product_list_with_selected_columns['高（cm）'].fillna(5)
tw_site_product_list_with_selected_columns['发货期'] = tw_site_product_list_with_selected_columns['发货期'].fillna(2)


# In[28]:

translate_currency = 458.61
profit_rate = 1.2
tw_site_product_list_with_selected_columns['价格'] = tw_site_product_list_with_selected_columns['价格'] * translate_currency / profit_rate


# In[29]:

# tw_site_product_list_with_selected_columns.head(5)


# In[30]:

from googletrans import Translator


# In[31]:

translator = Translator(service_urls=[
      'translate.google.com',
      'translate.google.co.kr',
    ])
# translator.translate('韩国', dest='ko').text


# In[32]:

# translations = translator.translate(['The quick brown fox', 'jumps over', 'the lazy dog'], dest='ko')
# for translation in translations:
#     print(translation.origin, ' -> ', translation.text)


# In[33]:

translate_columns = ['产品标题', '产品描述', '变种名称', '变种属性名称一', '变种属性名称二', '变种属性值一', '变种属性值二']
# translate_columns = ['产品标题']
# translate_columns = ['产品描述', '变种名称', '变种属性名称一', '变种属性名称二', '变种属性值一', '变种属性值二']


# In[34]:

# 把空值填充为string格式
tw_site_product_list_with_selected_columns[translate_columns] = tw_site_product_list_with_selected_columns[translate_columns].fillna(value='不需翻译')


# In[35]:

# 把variation_name做一些删减
variation_list = set(list(tw_site_product_list_with_selected_columns['变种属性名称一'].unique()) + list(tw_site_product_list_with_selected_columns['变种属性名称二'].unique()))
logging.info('variation list: ' + str(variation_list))


# In[36]:

variation_rename = {'适合身高': '身高', '童袜尺码': '尺码', '不需翻译': 'not set'}
tw_site_product_list_with_selected_columns['变种属性名称一'] = tw_site_product_list_with_selected_columns['变种属性名称一'].apply(lambda x: variation_rename[x] if x in variation_rename else x)
tw_site_product_list_with_selected_columns['变种属性名称二'] = tw_site_product_list_with_selected_columns['变种属性名称二'].apply(lambda x: variation_rename[x] if x in variation_rename else x)


# In[37]:

# 对variation_value做一些删减
# variation_value_list = set(list(tw_site_product_list_with_selected_columns['变种属性值一'].unique()) + list(tw_site_product_list_with_selected_columns['变种属性值一'].unique()))
# logging.info('variation value list: ' + str(variation_value_list))


# In[38]:

tw_site_product_list_with_selected_columns = tw_site_product_list_with_selected_columns[:5]
# # tw_site_product_list_with_selected_columns


# In[39]:

today = date.today()
d1 = today.strftime("%Y_%m_%d")


# In[40]:

# for index, row in tw_site_product_list_with_selected_columns.iterrows():
#     try:
#         list_to_translate = []
#         for i, value in enumerate(translate_columns):
#             list_to_translate.append(row[translate_columns[i]])
        
#         translate_language = 'en'
#         translator = Translator(service_urls=['translate.google.com'])
#         list_be_translated = translator.translate(list_to_translate, dest=translate_language, src='zh-CN')
#         # list_be_translated = translator.translate(list_to_translate, dest=translate_language)
#         time.sleep(10)
        
#         i = 0
#         for translate_language in list_be_translated:
#             tw_site_product_list_with_selected_columns.at[index, translate_columns[i]] = translate_language.text
#             i += 1
        
#         if (index + 1) % 5 == 0:
#             logging.info(str(index + 1) + ' rows have been translated.')
            
#         tw_site_product_list_with_selected_columns.to_excel(os.path.join(folder_path, 'translated_product_' + d1 + '.xlsx'), index=False)
#     except Exception as err:
#         logging.warning(str(index + 1) + ' rows have not been translated. Error message: ' + str(err))
#         pass


# In[41]:

for index, row in tw_site_product_list_with_selected_columns.iterrows():
    translated = 0
    while translated == 0:
        try:
            list_to_translate = []
            for i, value in enumerate(translate_columns):
                list_to_translate.append(row[translate_columns[i]])

            translate_language = 'id'
            translator = Translator(service_urls=['translate.google.com'])
            list_be_translated = translator.translate(list_to_translate, dest=translate_language, src='zh-CN')
            # list_be_translated = translator.translate(list_to_translate, dest=translate_language)
            time.sleep(10)

            i = 0
            for translate_language in list_be_translated:
                tw_site_product_list_with_selected_columns.at[index, translate_columns[i]] = translate_language.text
                i += 1

            if (index + 1) % 5 == 0:
                logging.info(str(index + 1) + ' rows have been translated.')

            tw_site_product_list_with_selected_columns.to_excel(os.path.join(folder_path, 'translated_product_id_' + d1 + '.xlsx'), index=False)
            translated = 1
        except Exception as err:
            logging.warning(str(index + 1) + ' rows have not been translated. Error message: ' + str(err) + ', try again.')
            pass        


# In[42]:

# for translate_column in translate_columns:
#     # tw_site_product_list_with_selected_columns[translate_column] = tw_site_product_list_with_selected_columns[translate_column].fillna(0)
#     # tw_site_product_list_with_selected_columns[translate_column]  = [translator.translate(x, dest=translate_language).text 
#                                                                      # for x in tw_site_product_list_with_selected_columns[translate_column]]
#     for index, row in tw_site_product_list_with_selected_columns.iterrows():
#         try:
#             orginal_text = tw_site_product_list_with_selected_columns.at[index, translate_column]
#             tw_site_product_list_with_selected_columns.at[index, translate_column] = translator.translate(row[translate_column], dest=translate_language).text
#             # print(row[translate_column])
#             logging.info(translate_column + ' - ' + str(index + 1) + ' rows have been translated.')
#             # logging.info(orginal_text + ' -> ' + tw_site_product_list_with_selected_columns.at[index, translate_column])
#             time.sleep(5)
#         except:
#             logging.warning(translate_column + ' - ' + str(index + 1) + ' rows have not been translated.')
#             pass
        
#     # print(tw_site_product_list_with_selected_columns.head(5))
    
#     tw_site_product_list_with_selected_columns.to_excel(os.path.join(folder_path, 'tw_translated_product(1).xlsx'), index=False)
#     logging.info(str(translate_column) + ' is done.')

