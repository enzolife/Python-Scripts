
# coding: utf-8

# In[266]:

import pandas as pd
import os
import time
import logging


# In[267]:

logging.basicConfig(level=logging.INFO, format=' %(asctime)s - %(levelname)s - %(message)s')


# In[268]:

folder_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\-E·J- 2014.5.1\\2019.7.24 tengus产品迁移\\'
tw_site_product_list = pd.read_excel(os.path.join(folder_path, 'tengus台湾站产品.xlsx'))


# In[269]:

# tw_site_product_list.columns


# In[270]:

# tw_site_product_list = tw_site_product_list[tw_site_product_list['产品id'] == 2496637042]


# In[271]:

top_cat_in_tw = tw_site_product_list[['分类ID', '产品id']].groupby('分类ID').agg({'产品id': 'nunique'}).reset_index().sort_values(by='产品id', ascending=False).reset_index().head(5)
# top_cat_in_tw


# In[272]:

top_cat_id = top_cat_in_tw['分类ID'][0]
top_cat_id


# In[273]:

output_excel_columns = ['变种名称',
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


# In[274]:

tw_site_product_list_selected_columns = ['分类ID', '产品属性', 'Parent SKU', '产品标题', '产品描述', 'sku', '变种名称', '变种属性名称一',
       '变种属性名称二', '变种属性值一', '变种属性值二', '价格', '库存', '重量', '主图（URL）地址', '附图1',
       '附图2', '附图3', '附图4', '附图5', '附图6', '附图7', '附图8地址', '变种图', '长（cm）',
       '宽（cm）', '高（cm）', '发货期', '来源URL', '尺码图']


# In[275]:

tw_site_product_list_with_selected_columns = tw_site_product_list[tw_site_product_list_selected_columns]
# tw_site_product_list_with_selected_columns.head(5)


# In[276]:

# tw_site_product_list_with_selected_columns = tw_site_product_list_with_selected_columns[tw_site_product_list_with_selected_columns['分类ID'] == top_cat_id].reset_index()
# tw_site_product_list_with_selected_columns


# In[277]:

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

remove_emoji('ins爆款 🥕胡蘿卜🥕寶寶針織竹節棉爬服 嬰兒兔裝 嬰兒連身衣 寶寶包屁衣連身衣 中間開襟包屁衣 寶寶連體衣哈衣爬服')


# In[278]:

tw_site_product_list_with_selected_columns['产品标题'] = [remove_emoji(x) for x in tw_site_product_list_with_selected_columns['产品标题']]
tw_site_product_list_with_selected_columns['产品描述'] = [remove_emoji(x) for x in tw_site_product_list_with_selected_columns['产品描述']]


# In[279]:

tw_site_product_list_with_selected_columns['长（cm）'] = tw_site_product_list_with_selected_columns['长（cm）'].fillna(18)
tw_site_product_list_with_selected_columns['宽（cm）'] = tw_site_product_list_with_selected_columns['宽（cm）'].fillna(13)
tw_site_product_list_with_selected_columns['高（cm）'] = tw_site_product_list_with_selected_columns['高（cm）'].fillna(5)
tw_site_product_list_with_selected_columns['发货期'] = tw_site_product_list_with_selected_columns['发货期'].fillna(2)


# In[280]:

translate_currency = 1
tw_site_product_list_with_selected_columns['价格'] = tw_site_product_list_with_selected_columns['价格'] * translate_currency


# In[281]:

# tw_site_product_list_with_selected_columns.head(5)


# In[282]:

from googletrans import Translator


# In[283]:

translator = Translator(service_urls=['translate.google.com'])
translator.translate('韩国', dest='ko').text


# In[284]:

translations = translator.translate(['The quick brown fox', 'jumps over', 'the lazy dog'], dest='ko')
for translation in translations:
    print(translation.origin, ' -> ', translation.text)


# In[285]:

translate_columns = ['产品标题', '产品描述', '变种名称', '变种属性名称一', '变种属性名称二', '变种属性值一', '变种属性值二']
# translate_columns = ['产品标题']
# translate_columns = ['产品描述', '变种名称', '变种属性名称一', '变种属性名称二', '变种属性值一', '变种属性值二']
translate_language = 'th'


# In[286]:

tw_site_product_list_with_selected_columns = tw_site_product_list_with_selected_columns[2:10]
# tw_site_product_list_with_selected_columns


# In[291]:

for index, row in tw_site_product_list_with_selected_columns.iterrows():
    try:
        list_to_translate = []
        for i, value in enumerate(translate_columns):
            list_to_translate.append(row[translate_columns[i]])
        
        translator = Translator(service_urls=['translate.google.com'])
        list_be_translated = translator.translate(list_to_translate, dest=translate_language)
        time.sleep(20)
        
        i = 0
        for translate_language in list_be_translated:
            tw_site_product_list_with_selected_columns.at[index, translate_columns[i]] = translate_language.text
            i += 1
        
        if (index + 1) % 5 == 0:
            logging.warning(str(index + 1) + ' rows have been translated.')
        
    except Exception as err:
        print(str(index + 1) + ' rows have not been translated. Error message: ' + str(err))
        pass
    
tw_site_product_list_with_selected_columns.to_excel(os.path.join(folder_path, 'tw_translated_product(1).xlsx'), index=False)


# In[288]:

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

