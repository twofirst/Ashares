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
collection_file = './Files/stock_rank_hs300_20090101-20181231_top100.csv'
start_date = '20180101'
end_date = '20181231'

astocks = data_download().get_Astocks()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
stocks = stocks.merge(astocks, on=['code', 'name'])
collection = pd.read_csv(collection_file)

# hs300_data = data_download().get_sz50_index(start_date, end_date, ma=[10, 20, 30, 120])
hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30, 120])
buy_ma = buy_stragy().ma_stragy
sell_ma = sell_stragy().ma_stragy

data = {}
for i in stocks.index[:]:
    code = stocks.ix[i, 'code']
    industry = stocks.ix[i, 'industry']

    if code == '600372' or code == '002044':
        continue

    if int(code) not in collection['code'].values:
        continue

    stock_data = data_download().get_stock_day_data(code, ma_list=[5, 10, 20, 30, 120], start_date=start_date,
                                                    end_date=end_date)
    if stock_data is not None:
        data[code] = stock_data

while True:
    stock_code = ''
    money = 1000000
    max_stock = 3
    in_stock_dict = {}  # {code:{share_cnt:0,invest:0,buy_date:0}}
    records = []

    for i in hs300_data.index:
        trade_date = hs300_data.ix[i, 'trade_date']
        hs300_close = hs300_data.ix[i, 'close']
        hs300_chg = hs300_data.ix[i, 'change']
        hs300_ma10 = hs300_data.ix[i, 'ma10']
        hs300_ma20 = hs300_data.ix[i, 'ma20']
        hs300_ma30 = hs300_data.ix[i, 'ma30']
        hs300_vol = hs300_data.ix[i, 'vol']
        hs300_ma_v_30 = hs300_data.ix[i, 'ma_v_30']
        hs300_ma_v_120 = hs300_data.ix[i, 'ma_v_120']

        flag = hs300_close > hs300_ma30 and hs300_ma_v_30 > hs300_ma_v_120

        if len(in_stock_dict) > 0:
            ls = list(in_stock_dict.keys())
            for stock_code in ls:
                stock_data = data.get(stock_code)
                if trade_date not in stock_data['trade_date'].values:
                    continue
                stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
                stock_close = stock_data.ix[stock_index, 'close']
                stock_ma5 = stock_data.ix[stock_index, 'ma5']
                stock_ma10 = stock_data.ix[stock_index, 'ma10']
                stock_ma20 = stock_data.ix[stock_index, 'ma20']
                stock_ma30 = stock_data.ix[stock_index, 'ma30']

                if stock_close > stock_ma20:
                    continue
                else:
                    value = stock_close * in_stock_dict.get(stock_code).get('share_cnt') * 100 * (1 - 0.002)
                    invest = in_stock_dict.get(stock_code).get('invest')
                    earn = value - invest
                    money += value
                    rate = round(earn / invest, 2)
                    buy_price = in_stock_dict.get(stock_code).get('buy_price')
                    buy_date = in_stock_dict.get(stock_code).get('buy_date')
                    record = [stock_code, buy_date, trade_date,
                              trade(None, None, None).calc_trade_days(buy_date, trade_date),
                              buy_price, stock_close, rate, money]
                    # print(stock_code,record)
                    records.append(record)
                    in_stock_dict.pop(stock_code)

        # elif hs300_close > hs300_ma30 and hs300_ma20>=hs300_ma30 and hs300_chg>0:
        if flag and len(in_stock_dict) < max_stock:
            candidates = []
            for key in data.keys():
                stock_data = data.get(key)
                if trade_date not in stock_data['trade_date'].values:
                    continue
                stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
                if stock_index == 0:
                    continue

                low = stock_data.ix[stock_index, 'low']
                high = stock_data.ix[stock_index, 'high']
                open = stock_data.ix[stock_index, 'open']
                close = stock_data.ix[stock_index, 'close']
                ma_20 = stock_data.ix[stock_index, 'ma20']
                ma_30 = stock_data.ix[stock_index, 'ma30']
                pre_close = stock_data.ix[stock_index - 1, 'close']
                pre_ma20 = stock_data.ix[stock_index - 1, 'ma20']
                pre_ma30 = stock_data.ix[stock_index - 1, 'ma30']
                vol = stock_data.ix[stock_index, 'vol']
                pre_vol = stock_data.ix[stock_index - 1, 'vol']
                change = stock_data.ix[stock_index, 'change']
                pct_chg = stock_data.ix[stock_index, 'pct_chg']

                bar_stop = True if open == close and low == high and close == low else False
                if pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol and close / ma_20 <= 1.05:
                    candidates.append(key)

            if len(candidates) == 0:
                continue
            targets = pd.DataFrame(candidates, columns=['stock_code']).sample(
                min(len(candidates), max_stock - len(in_stock_dict)))
            valid_money = money / (max_stock - len(in_stock_dict))

            for stock_code in targets['stock_code'].values:
                stock_data = data.get(stock_code)
                stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
                close = stock_data.ix[stock_index, 'close']
                share_cnt = math.modf(valid_money / (close * 100))[1]

                if share_cnt > 0:
                    invest = close * 100 * share_cnt
                    money -= invest
                    in_stock_flag = True
                    buy_date = trade_date
                    # {code:{share_cnt:0,invest:0,buy_date:0}}
                    in_stock_dict[stock_code] = {'share_cnt': share_cnt, 'invest': invest, 'buy_date': buy_date,
                                                 'buy_price': close}

    else:
        if len(in_stock_dict) > 0:
            ls = list(in_stock_dict.keys())
            for stock_code in ls:
                stock_data = data.get(stock_code)
                if trade_date not in stock_data['trade_date'].values:
                    invest = in_stock_dict.get(stock_code).get('invest')
                    money += invest
                    continue
                stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
                stock_close = stock_data.ix[stock_index, 'close']
                value = stock_close * in_stock_dict.get(stock_code).get('share_cnt') * 100 * (1 - 0.002)
                invest = in_stock_dict.get(stock_code).get('invest')
                earn = value - invest
                money += value
                rate = round(earn / invest, 2)
                buy_price = in_stock_dict.get(stock_code).get('buy_price')
                buy_date = in_stock_dict.get(stock_code).get('buy_date')
                record = [stock_code, buy_date, trade_date,
                          trade(None, None, None).calc_trade_days(buy_date, trade_date),
                          buy_price, stock_close, rate, money]
                # print(stock_code,record,'final')
                records.append(record)
                in_stock_dict.pop(stock_code)

    records = pd.DataFrame(records, columns=['code', 'buy_date', 'sell_date', 'days', 'buy_price', 'sell_price', 'rate',
                                             'money'])
    print('hs300 only collection', 'hs300_close > hs300_ma30 and hs300_ma_v_30 > hs300_ma_v_120',
          'close/ma_20<=1.05',
          'max_stock=',
          max_stock,
          start_date,
          end_date,
          len(records), records['rate'].min(), records['rate'].mean(), records['rate'].max(),
          money / 1000000, True if money > 1000000 else False)

    # if money / 1000000 > 15:
    #     print(records[['code', 'buy_date', 'sell_date', 'days', 'buy_price', 'sell_price', 'rate']])
