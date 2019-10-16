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
per_invest = 10000
invest_term_days = 70

astocks = data_download().get_Astocks()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
stocks = stocks.merge(astocks, on=['code', 'name'])

data = {}
for i in stocks.index[:]:
    total_invest = 0
    total_share = 0
    invest_times = 0
    code = stocks.ix[i, 'code']
    current_index = invest_term_days
    stock_data = data_download().get_stock_day_data(code, ma_list=[5], start_date=start_date, end_date=end_date)
    index_ls = stock_data.index.values

    while True:
        if current_index in index_ls:
            close = stock_data.ix[current_index, 'close']
            share_cnt = math.modf(per_invest / (close * 100))[1]
            total_share += share_cnt
            total_invest += share_cnt * 100 * close
            invest_times += 1
            current_index += invest_term_days
        else:
            break

    start_close = stock_data.head(1)['close'].values[0]
    end_close = stock_data.tail(1)['close'].values[0]
    end_value = total_share * 100 * end_close

    print(code, stocks[stocks['code'] == code]['name'].values[0], invest_times, total_invest, end_value,
          end_value / total_invest, end_close / start_close)
