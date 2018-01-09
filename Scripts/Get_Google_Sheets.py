import os
import csv
import gspread
import httplib2
import pandas as pd
import re
import time
from oauth2client.service_account import ServiceAccountCredentials
from Scripts.Get_Particular_Date import *
from itertools import islice


def get_access_token():
    scope = [
        'https://www.googleapis.com/auth/drive.metadata.readonly',
        'https://www.googleapis.com/auth/drive',
        'https://spreadsheets.google.com/feeds',
        'https://docs.google.com/feeds'
    ]

    credentials_path = "C://Users//Enzo.kuang//Documents//Python Scripts//Enzo Test Project-ea5529b41c25.json"
    # credentials_path = os.path.abspath('..\\Enzo Test Project-ea5529b41c25.json')
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_path, scope)
    # 重新刷新token，以防token失效
    try:
        gc = gspread.authorize(credentials)
        if credentials.access_token_expired:
            credentials.refresh(httplib2.Http())
            print('Access Token is refreshed.')
        return gc
    except Exception as e:
        print('An exception happened: ' + str(e))


# 下载Google Sheet到本地csv
def get_certain_google_sheets(list_of_google_sheet_name, output_path, selected_sheet):
    # sh = gc.create('2017.5.26 Test Google Sheet')
    # sh.share('enzo.kuang@shopeemobile.com', perm_type='user', role='writer')

    # Open Seller Index by Key
    # seller_index = gc.open_by_key('1VLYS6XmEjiI9UBEx4cG8YaBbAXDkTvoPc9NJb-m6ECQ')
    # worksheet = seller_index.sheet1

    # list_of_lists = worksheet.get_all_values()
    # list_of_lists

    gc = get_access_token()

    print('Google Sheet download start.')

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


# 下载Google Sheet到Data Frame
def get_certain_google_sheets_to_dataframe(book_name, selected_sheet):
    gc = get_access_token()

    print('Google Sheet to Data Frame start.')

    doc = gc.open(book_name)
    sheet = doc.worksheet(selected_sheet)

    gspread_data_frame = pd.DataFrame(sheet.get_all_records())

    print('Google Sheet to Data Frame finished.')

    return gspread_data_frame


# 上传Data Frame到Google Sheet
def upload_dataframe_to_google_sheet(data_frame, spread_sheet_id, wks_name):
    # d = [pd.Series([1., 2., 3.], index=['a', 'b', 'c']),
    # pd.Series([1., 2., 3., 4.], index=['a', 'b', 'c', 'd'])]
    # df = pd.DataFrame(d)

    # use full path to spreadsheet file
    # spreadsheet = '1Cg4tZbC1_HGMHK5lSdRewPFUTUHKD1Al2z1Oq1fK-4s'
    # or spreadsheet file id
    # spreadsheet = '1cIOgi90...'

    # wks_name = '工作表1'

    print('Data Frame to Google Sheet start.')

    try:
        upload(data_frame, spread_sheet_id, wks_name)
        # if spreadsheet already exists, all data of provided worksheet(or first as default)
        # will be replaced with data of given DataFrame, make sure that this is what you need!
    except Exception as err:
        print('An exception happened: ' + str(err) + ", upload fails. \nWait 60 second and try again.")
        time.sleep(60)
        upload(data_frame, spread_sheet_id, wks_name)

    print('Dataframe is uploaded to Google Sheet.')


# 不使用df2gspread上传data frame到google sheet
def upload(df, gfile="/New Spreadsheet", wks_name=None, chunk_size=1000,
           col_names=True, row_names=True, clean=True, credentials=None,
           start_cell='A1', df_size=False, new_sheet_dimensions=(1000, 100)):
    # access credentials
    # credentials = get_credentials(credentials)
    # auth for gspread
    # gc = gspread.authorize(credentials)

    gc = get_access_token()

    gc.open_by_key(gfile)
    gfile_id = gfile

    # Tuple of rows, cols in the dataframe.
    # If user did not explicitly specify to resize sheet to dataframe size
    # then for new sheets set it to new_sheet_dimensions, which is by default 1000x100
    if df_size:
        new_sheet_dimensions = (len(df), len(df.columns))

    wks = get_worksheet(gc, gfile_id, wks_name, write_access=True,
                        new_sheet_dimensions=new_sheet_dimensions)
    if clean:
        wks = clean_worksheet(wks, gfile_id, wks_name, credentials)

    start_col = re.split('(\d+)', start_cell)[0].upper()
    start_row = re.split('(\d+)', start_cell)[1]
    start_row_int, start_col_int = wks.get_int_addr(start_cell)

    # find last index and column name (A B ... Z AA AB ... AZ BA)
    num_rows = len(df.index) + 1 if col_names else len(df.index)
    last_idx_adjust = start_row_int - 1
    last_idx = num_rows + last_idx_adjust

    num_cols = len(df.columns) + 1 if row_names else len(df.columns)
    last_col_adjust = start_col_int - 1
    last_col_int = num_cols + last_col_adjust
    last_col = re.split('(\d+)', (wks.get_addr_int(1, last_col_int)))[0].upper()

    # If user requested to resize sheet to fit dataframe, go ahead and
    # resize larger or smaller to better match new size of pandas dataframe.
    # Otherwise, leave it the same size unless the sheet needs to be expanded
    # to accomodate a larger dataframe.
    if df_size:
        wks.resize(rows=len(df.index) + col_names, cols=len(df.columns) + row_names)
    if len(df.index) + col_names + last_idx_adjust > wks.row_count:
        wks.add_rows(len(df.index) - wks.row_count + col_names + last_idx_adjust)
    if len(df.columns) + row_names + last_col_adjust > wks.col_count:
        wks.add_cols(len(df.columns) - wks.col_count + row_names + last_col_adjust)

    # Define first cell for rows and columns
    first_col = re.split('(\d+)', (wks.get_addr_int(1, start_col_int + 1)))[0].upper() if row_names else start_col
    first_row = str(start_row_int + 1) if col_names else start_row

    # Addition of col names
    if col_names:
        cell_list = wks.range('%s%s:%s%s' % (first_col, start_row, last_col, start_row))
        for idx, cell in enumerate(cell_list):
            cell.value = df.columns.values[idx]
        wks.update_cells(cell_list)

    # Addition of row names
    if row_names:
        cell_list = wks.range('%s%s:%s%d' % (start_col, first_row, start_col, last_idx))
        for idx, cell in enumerate(cell_list):
            cell.value = df.index[idx]
        wks.update_cells(cell_list)

    # Addition of cell values
    cell_list = wks.range('%s%s:%s%d' % (
        first_col, first_row, last_col, last_idx))
    for j, idx in enumerate(df.index):
        for i, col in enumerate(df.columns.values):
            cell_list[i + j * len(df.columns.values)].value = df[col][idx]
    for cells in grouper(chunk_size, cell_list):
        wks.update_cells(list(cells))

    return wks


def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(islice(it, n))
        if not chunk:
            return
        yield chunk


def clean_worksheet(wks, gfile_id, wks_name, credentials):
    """DOCS..."""

    values = wks.get_all_values()
    if values:
        df_ = pd.DataFrame(index=range(len(values)),
                           columns=range(len(values[0])))
        df_ = df_.fillna('')
        wks = upload(df_, gfile_id, wks_name=wks_name,
                     col_names=False, row_names=False, clean=False,
                     credentials=credentials)
    return wks


def get_worksheet(gc, gfile_id, wks_name, write_access=False, new_sheet_dimensions=(1000, 100)):
    """DOCS..."""
    if wks_name is not None:
        wsheet_match = lambda wks: re.match(
            r"<Worksheet '%s' id:\S+>" % (wks_name), str(wks))
    try:
        spsh = gc.open_by_key(gfile_id)
        wkss = spsh.worksheets()
        # if worksheet name is not provided , take first worksheet
        if wks_name is None:
            wks = spsh.sheet1
        # if worksheet name provided and exist in given spreadsheet
        elif any(map(wsheet_match, wkss)):
            wks = spsh.worksheet(wks_name)
        else:
            if write_access == True:
                # rows, cols = new_sheet_dimensions
                wks = spsh.add_worksheet(wks_name, *new_sheet_dimensions)
            else:
                wks = None
    except gspread.httpsession.HTTPError as e:
        # logr.error('Status:', e.response.status)
        # logr.error('Reason:', e.response.reason)
        raise

    return wks


# 在google sheet的某个单元格添加last update time
def upload_last_update_time(spread_sheet_id, wks_name, cell):
    gc = get_access_token()

    print('Last update time update start.')
    workbook = gc.open_by_key(spread_sheet_id)
    worksheet = workbook.worksheet(wks_name)
    worksheet.update_acell(cell, get_current_datetime())
    print('Last update time update finish.')


if __name__ == "__main__":
    '''
    list_of_google_sheet_name = [
        {"doc": "New Shop Tracker"}
    ]
    output_path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\' \
                  'Shopee 2016.4.12\\2016.8.28 Seller Index Data\\'
    selected_sheet = ['SG', 'MY', 'TW', 'ID', 'TH']

    # print(os.getcwd())
    
    book_name = 'Seller_Index_from_Salesforce'
    select_sheet = 'Raw_Seller_Index'
    '''

    spread_sheet_id = '1-QAqrNES-Ecu7paSJi7yBoSklCr1WwCohz1cRFobRlM'
    wks_name = 'Description'
    cell = "D4"

    upload_last_update_time(spread_sheet_id, wks_name, cell)