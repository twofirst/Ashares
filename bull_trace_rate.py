import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylab import axes
from data_download import data_download

data = {}
show_num = 120
start_date = '20190101'
end_date = '20301231'
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

hs300_data['ding'] = None
for i in hs300_data.index[2:]:
    close_1 = hs300_data.ix[i - 1, 'close']
    close = hs300_data.ix[i, 'close']
    ma20_1 = hs300_data.ix[i - 1, 'ma20']
    rate_2 = hs300_data.ix[i - 2, 'mean']
    rate_1 = hs300_data.ix[i - 1, 'mean']
    rate = hs300_data.ix[i, 'mean']
    if rate_1 >= rate_2 and rate_1 >= rate and close_1 > ma20_1 and rate_1 >= 0.9:
        # hs300_data.ix[i-1,'ding']=rate_1
        hs300_data.ix[i - 1, 'ding'] = True

hs300_data['beili'] = None
ding_ls = []
pre_close, max_close, pre_rate, max_rate = 0, 0, 0, 0
for i in hs300_data.index:
    ding = hs300_data.ix[i, 'ding']
    if ding:
        close = hs300_data.ix[i, 'close']
        rate = hs300_data.ix[i, 'mean']
        if len(ding_ls) > 0:
            pre_close, pre_rate = ding_ls[-1]
        ding_ls.append((close, rate))

        # if close>pre_close and rate<pre_rate:
        if close > pre_close and rate / pre_rate < close / pre_close:
            hs300_data.ix[i, 'beili'] = close

a50_df['mean'] = a50_df.mean(axis=1)
a50_df['close'] = hs300_data['close']
a50_df['point'] = a50_df.apply(lambda x: get_point(x, 0.9), axis=1)

# tmp_df=hs300_data.merge(a50_df,on='trade_date')
# tmp_df.to_csv('Files/history_bull_trace.csv',index=False)

idx = 0
intervel = 120
# for i in np.arange(1, len(hs300_data)):
    # if i % intervel == 0:
    #     idx = i
    #     start = hs300_data.ix[i - intervel, 'trade_date']
    #     now = hs300_data.ix[i, 'trade_date']
    #     df = hs300_data.ix[i - intervel:i, :]
    #     fig, ax1 = plt.subplots()
    #     ax2 = ax1.twinx()  # mirror the ax1
    #
    #     ax2.plot(df['trade_date'], df['mean'], 'b-')
    #     ax1.plot(df['trade_date'], df['close'], 'k-')
    #     # ax1.scatter(df['trade_date'], df['flag'], c='r', marker='.', s=30)
    #     # ax1.scatter(df['trade_date'], df['ding'], c='b', marker='.', s=30)
    #     ax1.scatter(df['trade_date'], df['beili'], c='r', marker='.', s=30)
    #     plt.xticks(df['trade_date'], rotation=90)
    #     plt.savefig('PNG/HS300/' + start + '-' + now + '.png')
# else:
start = hs300_data.ix[idx, 'trade_date']
now = hs300_data.ix[len(hs300_data) - 1, 'trade_date']
df = hs300_data.ix[len(hs300_data) - show_num:, :]

fig, ax1 = plt.subplots()
ax1.plot(df['trade_date'], df['close'], 'k-')
plt.xticks(df['trade_date'], rotation=90)
ax2 = ax1.twinx()  # mirror the ax1
ax2.plot(df['trade_date'], df['mean'], 'b-')

# ax1.scatter(df['trade_date'], df['flag'], c='r', marker='.', s=30)
# ax1.scatter(df['trade_date'], df['ding'], c='b', marker='.', s=30)
# ax1.scatter(df['trade_date'], df['beili'], c='r', marker='.', s=30)

plt.savefig('PNG/HS300/' + start + '-' + now + '.png')
