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
a50_stocks = data_download().get_sz50()
hs300_stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
# stocks = stocks.merge(astocks, on=['code', 'name'])

# hs300_data = data_download().get_sz50_index(start_date, end_date, ma=[10, 20, 30, 120])
hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30, 120])
buy_ma = buy_stragy().ma_stragy
sell_ma = sell_stragy().ma_stragy

data = {}
for i in hs300_stocks.index[:]:
    code = hs300_stocks.ix[i, 'code']
    if code == '600372' or code == '002044':
        continue
    stock_data = data_download().load_stock_day_data(code, start_date, end_date)
    data[code] = stock_data


def get_flag(row):
    # if row['close'] > 0:
    if row['close'] > row['ma20']:
        # if row['close'] > row['ma30']:
        # if row['close'] > row['ma30'] and row['vol'] > row['ma_v_30']:
        # if row['close'] > row['ma30'] and row['vol'] > row['ma_v_60']:
        # if row['close'] > row['ma30'] and row['ma_v_30'] > row['ma_v_120']:
        # if row['close'] > row['ma30'] and row['ma_v_60'] > row['ma_v_120']:
        return 1
    else:
        return 0


def get_label(row):
    # if row['close'] > row['ma20']:
    # if row['close'] > row['ma30']:
    # if row['close'] > row['ma20'] and row['vol']>row['ma_v_30']:
    # if row['close'] > row['ma30'] and row['vol']>row['ma_v_30']:
    # if row['close'] > row['ma20'] and row['vol']>row['ma_v_120']:
    if row['close'] > row['ma30'] and row['vol'] > row['ma_v_120']:
        # if row['close'] > row['ma30'] and row['vol']>row['ma_v_120'] and row['ma_v_30'] > row['ma_v_120']:
        return 1
    else:
        return 0


def get_point(row):
    if row['mean'] >= 0.8:
        return 1
    else:
        return 0


df = hs300_data[['trade_date']]
for i in a50_stocks.index[:]:
    code = a50_stocks.ix[i, 'code']
    stock_data = data.get(code)
    if len(stock_data) > 0:
        stock_data['label'] = stock_data.apply(get_label, axis=1)
        stock_data = stock_data[['trade_date', 'label']]
        df = df.merge(stock_data, on='trade_date', how='outer')

hs300_data['mean'] = df.mean(axis=1)
hs300_data['point'] = hs300_data.apply(get_point, axis=1)
hs300_data['flag'] = hs300_data.apply(get_flag, axis=1)
hs300_data['ma20_flag'] = hs300_data['close'] > hs300_data['ma20']

while True:
    stock_code = ''
    money = 1000000
    max_stock = 3
    in_stock_dict = {}  # {code:{share_cnt:0,invest:0,buy_date:0}}
    records = []

    for i in hs300_data.index:
        trade_date = hs300_data.ix[i, 'trade_date']
        # flag=hs300_data.ix[i,'flag']
        # flag = hs300_data.ix[i, 'point']
        bull_flag = hs300_data.ix[i, 'flag'] + hs300_data.ix[i, 'point']
        ma20_flag = hs300_data.ix[i, 'ma20_flag']

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
        if (ma20_flag or bull_flag) and len(in_stock_dict) < max_stock:
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
                ma_v_30 = stock_data.ix[stock_index, 'ma_v_30']
                ma_v_120 = stock_data.ix[stock_index, 'ma_v_120']
                pre_vol = stock_data.ix[stock_index - 1, 'vol']
                change = stock_data.ix[stock_index, 'change']
                pct_chg = stock_data.ix[stock_index, 'pct_chg']

                bar_stop = True if open == close and low == high and close == low else False
                # if pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol:
                if bull_flag and pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol and close / pre_close <= 1.05:
                    candidates.append(key)
                # if pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol and close / pre_close <= 1.175 and close / pre_close > 1.075:
                # if pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol and vol > ma_v_120 and ma_v_30 > ma_v_120:
                elif ma20_flag and pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol and vol > ma_v_120 and ma_v_30 > ma_v_120 and close / pre_close <= 1.05:
                    # if pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol and vol > ma_v_120 and ma_v_30 > ma_v_120 and close / pre_close <= 1.05 and close / pre_close > 1.025:
                    # if pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol and vol>ma_v_120 and ma_v_30>ma_v_120 and close / pre_close <= 1.075 and close / pre_close > 1.05:
                    # if pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol and vol>ma_v_120 and ma_v_30>ma_v_120 and close / pre_close > 1.075:
                    candidates.append(key)

            if len(candidates) == 0:
                continue
            targets = pd.DataFrame(candidates, columns=['stock_code']).sample(
                min(len(candidates), max_stock - len(in_stock_dict)))
            valid_money = money / (max_stock - len(in_stock_dict))
            # valid_money = money / len(targets)

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
            # print('money=',money,'in_stock_len=',len(in_stock_dict))
            ls = list(in_stock_dict.keys())
            for stock_code in ls:
                stock_data = data.get(stock_code)
                if trade_date not in stock_data['trade_date'].values:
                    invest = in_stock_dict.get(stock_code).get('invest')
                    money += invest
                    # print('without trade_date,stock_code=',stock_code,'money=',money)
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
                # print(record)
                in_stock_dict.pop(stock_code)

    records = pd.DataFrame(records, columns=['code', 'buy_date', 'sell_date', 'days', 'buy_price', 'sell_price', 'rate',
                                             'money'])
    print('hs300 adaptation', 'hs300_close>hs300_ma30',
          'hs300_ma_v_30>hs300_ma_v_120',
          '80%>a50_ma20',
          'close>ma_20 and close / pre_close <= 1.05',
          'vol > pre_vol and vol > ma_v_120 and ma_v_30 > ma_v_120',
          'max_stock=', max_stock, start_date, end_date, len(records), records['rate'].min(), records['rate'].mean(),
          records['rate'].max(), money / 1000000, True if money > 1000000 else False)

    # if money / 1000000 > 15:
    #     print(records[['code', 'buy_date', 'sell_date', 'days', 'buy_price', 'sell_price', 'rate']])
