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
for code, stock_data in data.items():
    down_cnt = 0
    for i in stock_data.index[1:]:
        pre_open = stock_data.ix[i - 1, 'open']
        pre_close = stock_data.ix[i - 1, 'close']
        pre_low = stock_data.ix[i - 1, 'low']
        open = stock_data.ix[i, 'open']
        close = stock_data.ix[i, 'close']

        # if close

        if pre_open>pre_close and open>close:
            if close == pre_close:
                down_cnt = 0
                continue
            elif close < pre_close:
                down_cnt += 1
            else:
                if down_cnt > 0:
                    # if down_cnt==6:
                    #     pre_high=stock_data.ix[i-1, 'high']
                    #     pre_low=stock_data.ix[i-1, 'low']
                    #     rate=round((pre_close-pre_low)/(pre_high-pre_low),2)
                    #     rate_dict[rate] = (rate_dict[rate] + 1) if rate in rate_dict else 1
                    cnt_dict[down_cnt] = (cnt_dict[down_cnt] + 1) if down_cnt in cnt_dict else 1
                    down_cnt = 0
                else:
                    continue

print(cnt_dict)
print(rate_dict)
for k,v in rate_dict.items():
    print(k,v)