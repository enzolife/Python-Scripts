import csv
import gspread
import urllib
import codecs
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import os


def get_certain_google_sheets(list_of_google_sheet_name, output_path, selected_sheet):
    scope = [
        'https://spreadsheets.google.com/feeds',
        'https://www.googleapis.com/auth/drive'
    ]

    credentials_path = os.path.abspath('..\\Enzo Test Project-ea5529b41c25.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    gc = gspread.authorize(credentials)

    # sh = gc.create('2017.5.26 Test Google Sheet')
    # sh.share('enzo.kuang@shopeemobile.com', perm_type='user', role='writer')

    # Open Seller Index by Key
    # seller_index = gc.open_by_key('1VLYS6XmEjiI9UBEx4cG8YaBbAXDkTvoPc9NJb-m6ECQ')
    # worksheet = seller_index.sheet1

    # list_of_lists = worksheet.get_all_values()
    # list_of_lists

    docs = list_of_google_sheet_name
    path = output_path
    sheet = selected_sheet

    # process doc list
    for doc in docs:
        spreadsheet = gc.open(doc["doc"])
        for i, worksheet in enumerate(spreadsheet.worksheets()):
            # 只取需要的sheet
            if worksheet.title in sheet:
                filename = path + doc["doc"] + '-' + worksheet.title + '-' + '.csv'
                # newline = ''这部分，请参考evernote:
                # For use with the csv module, the Python 3 open should also have newline='' as a parameter [ref]
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    content = worksheet.get_all_values()
                    for row in content:
                        new_row = []
                        for record in row:
                            new_row.append(record)
                        try:
                            writer.writerow(new_row)
                        except (UnicodeEncodeError, UnicodeDecodeError):
                            print("Caught unicode error")
                print('== Finished Download: ' + filename + ' ==')
    print('====== FINISHED ======')

# list_of_google_sheet_name = [
    # {"doc": "New Shop Tracker"}
    # ]
# output_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
       # 'Shopee 2016.4.12\\2016.8.28 Seller Index Data\\'
# selected_sheet = ['SG', 'MY', 'TW', 'ID', 'TH']

# print(os.getcwd())
# get_certain_google_sheets(list_of_google_sheet_name, output_path, selected_sheet)
