import numpy as np
import pandas as pd
from data_download import data_download
from trade import trade
from stragy import buy_stragy, sell_stragy
from models import *

pd.set_option('display.max_columns', 99)
file = './Files/trade_info_hs300_20170101-20181231_more_features_1.csv'

start_date = '20090101'
end_date = '20181231'
# sz50 = data_download().get_sz50()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# sh_index = data_download().get_sh_index()
# sz_index = data_download().get_sz_index()
hs300_index = data_download().get_hs300_index('20050101', end_date, ma=[10, 20, 30, 60, 90, 120])

buy_ma = buy_stragy().ma_stragy
sell_ma = sell_stragy().ma_stragy

# records = pd.read_csv('./Files/trade_info_hs300_20050101-20151231.csv', header=0)
# records = records.dropna(axis=0)
#
# up = records[records['success'] == True]
# down = records[records['success'] == False]
# pos = records[records['success'] == True]
# neg = records[records['success'] == False]
#
# train_1 = pos.append(neg.sample(len(pos)))
# train_2 = up.append(down)
#
# train_1_X = train_1[train_1.columns[:-1]]
# train_2_X = train_2[train_2.columns[:-1]]
# train_1_y = train_1['success'] == True
# train_2_y = train_2['success'] == False
#
# clf_1 = train_classifier(train_1_X, train_1_y)
# clf_2 = train_classifier(train_2_X, train_2_y)
clf_1 = None
clf_2 = None

trade = trade(hs300_index, buy_ma, sell_ma)
for i in stocks.index:
    code = stocks.ix[i, 'code']
    name = stocks.ix[i, 'name']
    # if code!='000651':
    #     print(code,name)
    #     continue

    day_data = data_download().get_stock_day_data(code, ma_list=[5, 10, 20, 30, 60, 90, 120, 150],
                                                  start_date=start_date, end_date=end_date)
    week_data = data_download().get_stock_week_data(code, ma_list=[30])
    if len(day_data)==0:
        continue

    start_price = day_data.head(1)['close'].values[0]
    end_price = day_data.tail(1)['close'].values[0]
    in_stock_rate = (end_price - start_price) / start_price

    try:
        records = trade.buy_sell(day_data, week_data)
        # print(records)
        earn_rate = round((records['money'].values[-1] - trade.initial_money) / trade.initial_money, 2)
        print(code,name, 'rate_min=', records['earn_rate'].min(), 'rate_mean=', records['earn_rate'].mean(),
              'rate_max=',
              records['earn_rate'].max(), 'success_rate=', records['success'].mean(),
              'earn_rate=', earn_rate, 'in_stock_rate=', in_stock_rate,
              True if earn_rate > 0 and earn_rate > in_stock_rate else False)

        # print(trade.records)
    except:
        print(code, 'error')
        continue

        # trade.get_records_info().to_csv(file, index=False)
# else:
#     trade.get_records_info().to_csv(file, index=False)
# print(file)
print(
    'close > day_ma_price and vol>pre_vol and change>0 and not (pct_chg>=9.9 and high==close) and hs300_close>hs300_ma and hs300_index')
