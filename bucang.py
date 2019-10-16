import math
import numpy as np
import pandas as pd
from data_download import data_download
from trade import trade
from stragy import buy_stragy, sell_stragy
from models import *
from utils import calc_trade_days

pd.set_option('display.max_columns', 99)
pd.set_option('display.max_rows', 999)
file = './Files/simulator_hs300_20050101-20151231.csv'
start_date = '20070801'
end_date = '20191231'
per_invest = 100000
invest_term_days = 70
rate = 0.8

astocks = data_download().get_Astocks()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
# stocks = stocks.merge(astocks, on=['code', 'name'])
# stocks = astocks

print('code', 'name', 'start_day', 'end_day', 'days', 'invest_times', 'avg_price', 'close', 'total_share',
      'end_value', 'total_invest', 'cash', 'earn_rate', 'stock_rate', 'weighted_sell')
for i in stocks.index[:]:
    cash = 0
    weight = 999
    sell_value = 0
    total_invest = 0
    total_share = 0
    invest_times = 0
    avg_price = 999
    last_price = 999
    code = stocks.ix[i, 'code']
    name = stocks[stocks['code'] == code]['name'].values[0].replace(' ', '')
    # if code != '601857':
    #     continue
    stock_data = data_download().get_stock_day_data(code, ma_list=[5], start_date=start_date, end_date=end_date)
    if stock_data is None or len(stock_data) <= 280:
        continue
    start_day = stock_data.ix[invest_term_days, 'trade_date']
    end_day = 'CONTINUE'

    for i in stock_data.index[invest_term_days:]:
        if i % 23 == 0:
            cash += per_invest
        close = stock_data.ix[i, 'close']
        high = stock_data.ix[i, 'high']
        trade_date = stock_data.ix[i, 'trade_date']

        if cash >= close * 100 and (close < last_price * rate or (i % invest_term_days == 0 and close < avg_price)):
            invest_weight = avg_price / close
            share_cnt = math.modf(np.fmin(cash, per_invest * invest_weight) / (close * 100))[1]
            invest = share_cnt * 100 * close
            total_share += share_cnt
            total_invest += invest
            invest_times += 1
            cash -= invest
            avg_price = total_invest / (total_share * 100)
            last_price = close
            # print('buy', trade_date, invest_times, close, share_cnt, invest, avg_price, total_share, total_invest,
            #       (total_share * 100 * close) / total_invest)
        elif invest_times > 0 and avg_price != 0:
            # weight = 1 / np.log2(invest_times + 1) + 1
            weight=2
            sell_price = round(avg_price * weight, 2)
            if high > sell_price:
                sell_share = math.modf(total_share / weight)[1]
                total_share -= sell_share
                sell_value = sell_share * 100 * sell_price
                cash += sell_value
                # invest_times += 1
                avg_price = 0
                end_day = trade_date
                # print('sell', trade_date, invest_times, sell_price, sell_share, cash, avg_price, total_share,
                #       total_invest, 1 / weight)
                break

    if total_invest == 0 or total_share == 0:
        # print('error!', code, stocks[stocks['code'] == code]['name'].values[0], invest_times, avg_price)
        continue
    start_close = stock_data.head(1)['close'].values[0]
    end_close = stock_data.tail(1)['close'].values[0]
    end_value = total_share * 100 * end_close
    if end_day != 'CONTINUE':
        days = calc_trade_days(start_day, end_day)
    else:
        days = calc_trade_days(start_day, end_date)

    print(code, name, start_day, end_day, days, invest_times,
          avg_price, end_close, total_share, end_value, total_invest, cash, (end_value + sell_value) / total_invest,
          end_close / start_close, 1 / weight)
