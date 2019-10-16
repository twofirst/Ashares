import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylab import axes
from data_download import data_download

data = {}
start_date = '20090101'
end_date = '20181231'
# end_date = '20190328'
# astocks = data_download().get_Astocks()
a50_stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
# hs300_data = data_download().get_sz50_index(start_date, end_date, ma=[20, 30, 60, 120])
hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[20, 30, 60, 120])


def get_flag(row, rate):
    # if row['close'] > row['ma30'] and row['vol'] > row['ma_v_30']:
    # if row['close'] > row['ma30'] and row['vol'] > row['ma_v_60']:
    if row['close'] > row['ma30'] and row['ma_v_30'] > row['ma_v_120']:
        # if row['close'] > row['ma30'] and row['ma_v_60'] > row['ma_v_120']:
        return row['close'] * rate
    else:
        return None


def get_label(row):
    if row['close'] > row['ma20']:
        # if row['close'] > row['ma30']:
        # if row['ma_v_30'] > row['ma_v_120']:
        # if row['vol'] > row['ma_v_30'] and row['ma_v_30'] > row['ma_v_120']:
        # if row['ma5'] < row['ma10'] and row['ma10']<row['ma20']:
        # if row['close'] > row['ma30'] and row['vol']>row['ma_v_30']:
        # if row['close'] > row['ma20'] and row['vol']>row['ma_v_120']:
        # if row['close'] > row['ma30'] and row['vol']>row['ma_v_120']:
        # if row['close'] > row['ma30'] and row['vol']>row['ma_v_120'] and row['ma_v_30'] > row['ma_v_120']:
        return 1
    else:
        return 0


def get_point(row, rate):
    if row['mean'] >= rate:
        return row['close'] * rate
    else:
        return None


def get_high(row, rate):
    if row['mean'] >= 0.7:
        return row['close'] * rate
    else:
        return 0


def get_low(row):
    if row['mean'] <= 0.05:
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
hs300_data['flag'] = hs300_data.apply(lambda x: get_flag(x, 1), axis=1)
# hs300_data['0.9'] = hs300_data.apply(lambda x: get_point(x, 0.9), axis=1)
# hs300_data['0.8'] = hs300_data.apply(lambda x: get_point(x, 0.8), axis=1)
hs300_data['0.7'] = hs300_data.apply(lambda x: get_point(x, 0.7), axis=1)
# hs300_data['0.6'] = hs300_data.apply(lambda x: get_point(x, 0.6), axis=1)
# hs300_data['0.5'] = hs300_data.apply(lambda x: get_point(x, 0.5), axis=1)
# hs300_data['high'] = hs300_data.apply(lambda x:get_high(x,0.7), axis=1)
hs300_data['low'] = hs300_data.apply(lambda x:get_low(x), axis=1)
hs300_data['and'] = ((hs300_data['flag'] > 0) & (hs300_data['0.7'] > 0)) * hs300_data['close'] * 1.2
hs300_data['and']=hs300_data['and'].apply(lambda x: None if x==0 else x)

a50_df['mean'] = a50_df.mean(axis=1)
a50_df['close'] = hs300_data['close']
a50_df['a50_0.9'] = a50_df.apply(lambda x: get_point(x, 0.9), axis=1)
a50_df['a50_0.9'] = a50_df['a50_0.9'] * 1.5
# a50_df['a50_0.8'] = a50_df.apply(lambda x: get_point(x, 0.8), axis=1)
# a50_df['a50_0.8'] = a50_df['a50_0.8'] * 2

fig, ax1 = plt.subplots()
# ax2 = ax1.twinx()  # mirror the ax1

# ax1.plot(hs300_data['trade_date'], hs300_data['close'] * 1.2, 'k-')
# ax1.scatter(hs300_data['trade_date'], hs300_data['and'], c='r', marker='.')
ax1.plot(hs300_data['trade_date'], hs300_data['close'], 'k-')
ax1.scatter(hs300_data['trade_date'], hs300_data['flag'], c='b', marker='.')
# ax1.plot(hs300_data['trade_date'], hs300_data['close'] * 0.9, 'b-')
# ax1.scatter(hs300_data['trade_date'], hs300_data['0.9'], c='r', marker='.')
# ax1.plot(hs300_data['trade_date'], hs300_data['close'] * 0.8, 'b-')
# ax1.scatter(hs300_data['trade_date'], hs300_data['0.8'], c='r', marker='.')
# ax1.plot(hs300_data['trade_date'], hs300_data['close'] * 0.7, 'k-')
# ax1.scatter(hs300_data['trade_date'], hs300_data['0.7'], c='g', marker='+')
# ax1.plot(hs300_data['trade_date'], hs300_data['close'] * 0.6, 'b-')
# ax1.scatter(hs300_data['trade_date'], hs300_data['0.6'], c='r', marker='.')
# ax1.plot(hs300_data['trade_date'], hs300_data['close'] * 0.5, 'b-')
# ax1.scatter(hs300_data['trade_date'], hs300_data['0.5'], c='r', marker='.')
# ax1.plot(hs300_data['trade_date'], hs300_data['close'] * 1.35, 'k-')
# ax1.scatter(hs300_data['trade_date'], a50_df['a50_0.9'], c='y', marker='x')
# ax1.plot(hs300_data['trade_date'], hs300_data['close'], 'k-')
# ax1.scatter(hs300_data['trade_date'], hs300_data['low'], c='r', marker='+')

plt.show()
