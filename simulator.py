import math
import numpy as np
import pandas as pd
from data_download import data_download
from trade import trade
from stragy import buy_stragy, sell_stragy
from models import *

pd.set_option('display.max_columns', 99)
file = './Files/simulator_hs300_20050101-20151231.csv'
start_date = '20090101'
end_date = '20181231'

stocks = data_download().get_hs300()
hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30, 120])
buy_ma = buy_stragy().ma_stragy
sell_ma = sell_stragy().ma_stragy

data = {}
for i in stocks.index:
    code = stocks.ix[i, 'code']
    stock_data = data_download().get_stock_day_data(code, ma_list=[20, 30], start_date=start_date, end_date=end_date)
    if stock_data is not None:
        data[code] = stock_data

while True:
    stock_code = ''
    money = 1000000
    share_cnt = 0
    invest = 0
    value = 0
    buy_date = ''
    in_stock_flag = False
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

        flag = hs300_close > hs300_ma30 and hs300_vol > hs300_ma_v_120 and hs300_ma_v_30 > hs300_ma_v_120
        ma_status = trend().ma_up2(data=hs300_data, trade_date=trade_date, period=10, ma='ma_v_120')

        if in_stock_flag:
            stock_data = data.get(stock_code)
            if trade_date not in stock_data['trade_date'].values:
                continue
            stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
            stock_close = stock_data.ix[stock_index, 'close']
            stock_ma30 = stock_data.ix[stock_index, 'ma30']

            if stock_close > stock_ma30:
                continue
            else:
                value = stock_close * share_cnt * 100 * (1 - 0.002)
                earn = value - invest
                money += value
                rate = round(earn / invest, 2)
                record = [stock_code, buy_date, trade_date,
                          trade(None, None, None).calc_trade_days(buy_date, trade_date), rate, money]
                # print(record)
                records.append(record)
                share_cnt = 0
                invest = 0
                value = 0
                in_stock_flag = False

        # elif hs300_close > hs300_ma30 and hs300_ma20>=hs300_ma30 and hs300_chg>0:
        elif flag:
            # else:
            for key in data.keys():
                stock_data = data.get(key)
                if trade_date not in stock_data['trade_date'].values:
                    continue
                stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
                if stock_index == 0:
                    continue

                high = stock_data.ix[stock_index, 'high']
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

                if pre_close < pre_ma30 and close > ma_30 and vol > pre_vol and \
                        change > 0 and not (pct_chg >= 9.9 and high == close):
                    if np.random.randint(100) % 3 != 0:
                        print('pass')
                        continue

                    share_cnt = math.modf(money / (close * 100))[1]
                    if share_cnt > 0:
                        invest = close * 100 * share_cnt
                        money -= invest
                        in_stock_flag = True
                        buy_date = trade_date
                        stock_code = key
                        break
                else:
                    print('share_cnt:',share_cnt)
                    continue
            else:
                continue
    if share_cnt > 0:
        value = stock_close * 100 * share_cnt
        money += value
    records = pd.DataFrame(records, columns=['code', 'buy_date', 'sell_date', 'days', 'rate', 'money'])
    print(start_date, end_date, len(records), records['rate'].min(), records['rate'].mean(), records['rate'].max(),
          money / 1000000, True if money > 1000000 else False)
