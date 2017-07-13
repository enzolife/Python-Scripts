from df2gspread import gspread2df as g2d

# use full path to spreadsheet file
spreadsheet = '1VLYS6XmEjiI9UBEx4cG8YaBbAXDkTvoPc9NJb-m6ECQ'
# or spreadsheet file id
# spreadsheet = '1cIOgi90...'
wks_name = 'SG'

df = g2d.download(spreadsheet, wks_name, col_names=True, row_names=True)
