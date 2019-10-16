import math
import numpy as np
import pandas as pd
from data_download import data_download
from trend import trend
from trade import trade
from stragy import buy_stragy, sell_stragy
from models import *

pd.set_option('display.max_columns', 99)
file = './Files/simulator_20050101-20151231.csv'
start_date = '20170101'
end_date = '20181231'
money = 10000000
share_cnt = 0
invest = 0
value = 0
buy_date = ''
in_stock_flag = False

data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30,60,90,120])

for i in data.index[10:]:
    trade_date = data.ix[i, 'trade_date']
    close = data.ix[i, 'close']
    pre_close = data.ix[i-1, 'close']
    chg = data.ix[i, 'change']
    ma10 = data.ix[i, 'ma10']
    ma20 = data.ix[i, 'ma20']
    ma30 = data.ix[i, 'ma30']
    # ma_status = trend().ma_up2(data=data, trade_date=trade_date, period=3, ma='ma_v_120')
    vol=data.ix[i, 'vol']
    pre_vol=data.ix[i-1, 'vol']
    ma_v_30=data.ix[i, 'ma_v_30']
    ma_v_120=data.ix[i, 'ma_v_120']

    flag= vol>ma_v_120 and ma_v_30>ma_v_120
    # print(flag)

    if not in_stock_flag and close > ma30 and flag:
        share_cnt = math.modf(money / (close * 100))[1]
        # ma_status=trend().ma_up(data=data,trade_date=trade_date,period=10,ma='ma120')
        r='ma_status'

        if share_cnt > 0:
            invest = close * 100 * share_cnt
            money -= invest
            in_stock_flag = True
            buy_date = trade_date
    elif in_stock_flag and close < ma30:
        stock_value = close * 100 * share_cnt * (1 - 0.002)
        rate = round((stock_value - invest) / (money + invest), 2)
        success = True if rate > 0 else False
        money += stock_value
        share_cnt = 0
        in_stock_flag = False
        sell_date = trade_date
        days = trade(None, None, None).calc_trade_days(buy_date, sell_date)
        print(buy_date, sell_date, days, rate, success, money,r)
else:
    if in_stock_flag:
        stock_value = close * 100 * share_cnt * (1 - 0.002)
        rate = round((stock_value - invest) / (money + invest), 2)
        success = True if rate > 0 else False
        money += stock_value
        share_cnt = 0
        in_stock_flag = False
        sell_date = trade_date
        days = trade(None, None, None).calc_trade_days(buy_date, sell_date)
        print(buy_date, sell_date, days, rate, success, money,r)
    print(money/10000000)