import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data_download import data_download

data = {}
start_date = '20090101'
end_date = '20181231'
hs300_stocks = data_download().get_hs300()
for i in hs300_stocks.index[:]:
    code = hs300_stocks.ix[i, 'code']
    stock_data = data_download().load_stock_day_data(code, start_date, end_date)
    data[code] = stock_data

cnt_dict = {}
rate_dict = {}
pos_cnt = 0
neg_cnt = 0
for code, stock_data in data.items():
    shape_cnt = 0
    for i in stock_data.index[2:]:
        date = stock_data.ix[i, 'trade_date']
        # pre_5_low = stock_data.ix[i - 5, 'low']
        # pre_5_high = stock_data.ix[i - 5, 'high']
        # pre_4_low = stock_data.ix[i - 4, 'low']
        # pre_4_high = stock_data.ix[i - 4, 'high']
        # pre_3_low = stock_data.ix[i - 3, 'low']
        # pre_3_high = stock_data.ix[i - 3, 'high']
        pre_2_low = stock_data.ix[i - 2, 'low']
        pre_2_high = stock_data.ix[i - 2, 'high']
        pre_1_low = stock_data.ix[i - 1, 'low']
        pre_1_high = stock_data.ix[i - 1, 'high']
        pre_open = stock_data.ix[i - 1, 'open']
        pre_close = stock_data.ix[i - 1, 'close']
        open = stock_data.ix[i, 'open']
        close = stock_data.ix[i, 'close']
        low = stock_data.ix[i, 'low']

        if pre_2_high>pre_1_high and pre_2_low>pre_1_low and pre_close>pre_open and pre_close>pre_1_low:
            if close > pre_close:
                pos_cnt += 1
                print(code, date, close)
            else:
                neg_cnt += 1

print(pos_cnt, neg_cnt)
