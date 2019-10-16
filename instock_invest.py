import math
import numpy as np
import pandas as pd
from data_download import data_download
from trade import trade
from stragy import buy_stragy, sell_stragy
from models import *

pd.set_option('display.max_columns', 99)
pd.set_option('display.max_rows', 999)
file = './Files/simulator_hs300_20050101-20151231.csv'
start_date = '20090101'
end_date = '20181231'

astocks = data_download().get_Astocks()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
stocks = stocks.merge(astocks, on=['code', 'name'])

data = {}
for i in stocks.index[:]:
    code = stocks.ix[i, 'code']
    stock_data = data_download().load_stock_day_data(code, start_date=start_date, end_date=end_date)
    date_start = stock_data.head(1)['trade_date'].values[0]
    if '2009' in date_start:
        start_close = stock_data.head(1)['close'].values[0]
        date_end = stock_data.tail(1)['trade_date'].values[0]
        end_close = stock_data.tail(1)['close'].values[0]
        rate = end_close / start_close

        print(code, stocks[stocks['code'] == code]['name'].values[0], date_start, start_close, date_end, end_close,
              rate)
