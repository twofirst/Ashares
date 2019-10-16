import math
import numpy as np
import pandas as pd
from data_download import data_download
from trade import trade
from stragy import buy_stragy, sell_stragy
from models import *

pd.set_option('display.max_columns', 99)
pd.set_option('display.max_rows', 999)
file = './Files/simulator_hs300_20070801-20181231.csv'
start_date = '20090101'
end_date = '20191231'

astocks = data_download().get_Astocks()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
stocks = stocks.merge(astocks, on=['code', 'name'])
# stocks=astocks
hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10])

data = {}
for i in stocks.index[:]:
    code = stocks.ix[i, 'code']
    stock_data = data_download().get_stock_day_data(code, ma_list=[5], start_date='20000801', end_date=end_date)
    if stock_data is not None:
        data[code] = stock_data


def select_stock(trade_date):
    sort = []
    for code, stock_data in data.items():
        if trade_date in stock_data['trade_date'].values:
            df = stock_data[stock_data['trade_date'] <= trade_date]
            current_close = df.tail(1)['close'].values[0]
            max_close = df['close'].max()
            rate = current_close / max_close
            sort.append([code, rate])
    else:
        sort = pd.DataFrame(sort, columns=['code', 'rate'])
        sort.sort_values(by='rate', inplace=True)
        sort.reset_index(drop=True, inplace=True)

    return sort.ix[np.random.randint(int(len(data) * 0.2)), 'code']


while True:
    cash = 0
    weight = 999
    avg_price = 999
    total_money = 0
    total_share = 0
    invest_times = 0
    total_invest = 0
    invest_term_days = 70
    monthly_invest = 10000
    per_invest = monthly_invest
    in_stock_dict = {}  # {code:{name:'', invest_times:0, total_share:0,value:0, total_invest:0,buy_date:'',sell_date:''}}

    current_stock_code = None
    current_stock_name = None
    current_stock_data = None
    for hs_idx in hs300_data.index:
        if hs_idx % 23 == 0:
            cash += monthly_invest
            total_money += monthly_invest

        current_date = hs300_data.ix[hs_idx, 'trade_date']

        while current_stock_code is None:
            weight = 999
            avg_price = 999
            total_share = 0
            invest_times = 0
            total_invest = 0
            # per_invest = monthly_invest + int(cash * 1)
            per_invest = monthly_invest + int(cash * 0.25)
            code = select_stock(current_date)

            if code in in_stock_dict:
                continue

            stock_name = stocks[stocks['code'] == code]['name'].values[0]
            stock_data = data.get(code)
            # stock_data = data_download().get_stock_day_data(code, ma_list=[5], start_date='20000801', end_date=end_date)

            if stock_data is None or current_date not in stock_data['trade_date'].values:
                continue

            current_idx = stock_data[stock_data['trade_date'] == current_date].index.values[0]
            if current_idx <= invest_term_days:
                continue  # new stock

            close = stock_data.ix[current_idx, 'close']
            share_cnt = math.modf(per_invest / (close * 100))[1]
            if share_cnt == 0:
                continue

            current_stock_code = code
            current_stock_name = stock_name
            current_stock_data = stock_data
            # print(current_stock_code, current_stock_name)

        if current_date not in current_stock_data['trade_date'].values:
            continue
        idx = current_stock_data[current_stock_data['trade_date'] == current_date].index.values[0]
        close = current_stock_data.ix[idx, 'close']
        high = current_stock_data.ix[idx, 'high']
        trade_date = current_stock_data.ix[idx, 'trade_date']
        # weight = 1 / np.log2(np.fmax(invest_times, 1) + 1) + 1
        weight = 2.0
        sell_price = round(avg_price * weight, 2)

        if total_share == 0:
            buy_date = trade_date

        if hs_idx % invest_term_days == 0 and close < avg_price:
            invest_weight = avg_price / close
            per_invest = per_invest * invest_weight
            if cash <= per_invest:
                per_invest = cash
            share_cnt = math.modf(per_invest / (close * 100))[1]
            invest = share_cnt * 100 * close
            total_share += share_cnt
            total_invest += invest
            invest_times += 1
            cash -= invest
            avg_price = total_invest / (total_share * 100)
            # print('buy', trade_date, invest_times, close, share_cnt, invest, avg_price, total_share, total_invest, cash,
            #       (total_share * 100 * close) / total_invest)
        elif high > sell_price:
            value = total_share * 100 * sell_price
            cash += value
            sell_date = trade_date
            current_stock_code = None
            # print('sell', trade_date, sell_price, total_share, value, total_invest, cash, weight)
            # print(code, total_money, cash / total_money)
    else:
        profit = 0
        total_value = current_stock_data.tail(1)['close'].values[0] * total_share * 100
        for code, rcd in in_stock_dict.items():
            share_cnt = rcd['total_share']
            stock_data = data.get(code)
            profit += stock_data.tail(1)['close'].values[0] * share_cnt * 100
        else:
            total_value += profit
        print(total_money, cash, total_value, (cash + total_value) / total_money, profit)
        # print('*****************************************************')
