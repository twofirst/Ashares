import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylab import axes
from data_download import data_download

data = {}
show_num = 150
start_date = '20190101'
end_date = '20291231'
a50_stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[20, 30, 60, 120])


def get_flag(row):
    if row['close'] > row['ma30'] and row['ma_v_30'] > row['ma_v_120']:
        return row['close']
    else:
        return None


def get_label(row):
    if row['close'] > row['ma20']:
        return 1
    else:
        return 0


def get_point(row, rate):
    if row['mean'] >= rate:
        return row['close']
    else:
        return None


df = hs300_data[['trade_date']]
a50_df = hs300_data[['trade_date']]
for i in stocks.index[:]:
    code = stocks.ix[i, 'code']
    stock_data = data_download().load_stock_day_data(code, start_date, end_date)
    if len(stock_data) > 0:
        stock_data['label'] = stock_data.apply(get_label, axis=1)
        stock_data = stock_data[['trade_date', 'label']]
        df = df.merge(stock_data, on='trade_date', how='outer')
        if code in a50_stocks['code'].values:
            a50_df = a50_df.merge(stock_data, on='trade_date', how='outer')

hs300_data['mean'] = df.mean(axis=1)
hs300_data['flag'] = hs300_data.apply(get_flag, axis=1)
hs300_data['point'] = hs300_data.apply(lambda x: get_point(x, 0.7), axis=1)

a50_df['mean'] = a50_df.mean(axis=1)
a50_df['close'] = hs300_data['close']
a50_df['point'] = a50_df.apply(lambda x: get_point(x, 0.9), axis=1)

# tmp_df=hs300_data.merge(a50_df,on='trade_date')
# tmp_df.to_csv('Files/history_bull_trace.csv',index=False)

hs300_data = hs300_data.tail(show_num)
a50_df = a50_df.tail(show_num)
fig, ax1 = plt.subplots()

ax1.plot(hs300_data['trade_date'], hs300_data['close'], 'k-')
fig1 = ax1.scatter(hs300_data['trade_date'], a50_df['point'], c='g', marker='+', s=60)
fig2 = ax1.scatter(hs300_data['trade_date'], hs300_data['point'], c='b', marker='x', s=60)
fig3 = ax1.scatter(hs300_data['trade_date'], hs300_data['flag'], c='r', marker='.', s=30)
plt.legend((fig1, fig2, fig3), ('A50 Trace', 'HS300 Trace', 'Bull Market'))
plt.xticks(hs300_data['trade_date'], rotation=90)
plt.savefig('PNG/HS300/bull_trace.png')
# plt.show()
