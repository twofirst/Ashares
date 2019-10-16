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
code='000001.SZ'
start_date = '20100101'
end_date = '20181231'
money = 10000000
share_cnt = 0
invest = 0
value = 0
buy_date = ''
in_stock_flag = False

hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30,60,90,120])
data = data_download().get_stock_day_data(code,[10, 20, 30,60,90,120],start_date, end_date)

for i in data.index[1:]:
    trade_date = data.ix[i, 'trade_date']
    high = data.ix[i, 'high']
    close = data.ix[i, 'close']
    vol = data.ix[i, 'vol']
    pre_vol = data.ix[i-1, 'vol']
    change = data.ix[i, 'change']
    pct_chg = data.ix[i, 'pct_chg']
    ma10 = data.ix[i, 'ma10']
    ma20 = data.ix[i, 'ma20']
    ma30 = data.ix[i, 'ma30']
    ma_status = trend().ma_up2(data=hs300_data, trade_date=trade_date, period=10, ma='ma_v_120')

    # if not in_stock_flag and close > ma30 and vol>pre_vol and change>0 and not (pct_chg>=9.9 and high==close):
    if not in_stock_flag and close > ma30 and vol>pre_vol and change>0 and not (pct_chg>=9.9 and high==close) and ma_status[1]<=1:
        share_cnt = math.modf(money / (close * 100))[1]
        # ma_status=trend().ma_up(data=data,trade_date=trade_date,period=3,ma='ma120')
        r=ma_status

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