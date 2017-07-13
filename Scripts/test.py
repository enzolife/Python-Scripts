from pandas import Series, DataFrame
import pandas as pd
import glob
import os

path = 'D:\\Program Files (x86)\\百度云同步盘\\Dropbox\\Shopee 2016.4.12\\' \
       '2016.4.23 Data Visualization\\Listing'  # use your path
allFiles = glob.glob(path + "\\*\\*.csv")
frame = pd.DataFrame()
list_ = []
for file_ in allFiles:
    os.chdir(os.path.dirname(file_))
    df = pd.read_csv(os.path.basename(file_), index_col=None, header=0)
    print('file name: ' + os.path.basename(file_) + ' max date ' + df['Date Created'].values.max())
    print('file name: ' + os.path.basename(file_) + ' min date ' + df['Date Created'].values.min())
    print(df.shape)
    # print(file_)
    # list_.append(df)
# frame = pd.concat(list_)

# frame['Date Created'] = pd.to_datetime(frame['Date Created'])
# frame['year/month'] = frame['Date Created'].dt.strftime('%Y-%m')

# grouped = frame['Product ID'].groupby([frame['year/month'], frame['Country']])
# listing_by_month = grouped.agg({'Product ID': {'New SKUs': 'count'}})

# print(listing_by_month)