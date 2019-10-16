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
monthly_invest = 10000
invest_term_days = 70
max_stock = 10

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


def select_stock(trade_date, in_stock_dict, out_stock_dict, invest):
    sort = []
    for code, stock_data in data.items():
        if code not in in_stock_dict and code not in out_stock_dict and trade_date in stock_data['trade_date'].values:
            df = stock_data[stock_data['trade_date'] <= trade_date]
            if len(df) <= invest_term_days:
                continue  # new stock
            current_close = df.tail(1)['close'].values[0]
            share_cnt = math.modf(invest / (current_close * 100))[1]
            if share_cnt == 0:
                continue
            max_close = df['close'].max()
            rate = current_close / max_close
            sort.append([code, rate])
    else:
        sort = pd.DataFrame(sort, columns=['code', 'rate'])
        sort.sort_values(by='rate', inplace=True)
        sort.reset_index(drop=True, inplace=True)

    try:
        code = sort.ix[np.random.randint(int(len(sort) * 0.2)), 'code']
    except:
        print(sort)

    return code


def buy_new_stock(trade_date, in_stock_dict, out_stock_dict, per_invest):
    code = select_stock(trade_date, in_stock_dict, out_stock_dict, per_invest)
    name = stocks[stocks['code'] == code]['name'].values[0]
    stock_data = data.get(code)
    current_idx = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
    close = stock_data.ix[current_idx, 'close']
    share_cnt = math.modf(per_invest / (close * 100))[1]
    invest = share_cnt * 100 * close
    in_stock_dict[code] = {'name': name, 'invest_times': 1, 'total_share': share_cnt, 'avg_price': close,
                           'total_invest': invest, 'buy_date': trade_date, 'last_date_idx': current_idx}
    # print(code, name, 'buy', current_date, 1, close, share_cnt, invest, close, share_cnt, invest, 1)

    return invest


def trade_stock(current_date, code, in_stock_dict, out_stock_dict, per_invest):
    current_stock_data = data.get(code)
    if current_date in current_stock_data['trade_date'].values:
        _dict = in_stock_dict[code]
        stock_name = _dict['name']
        buy_date = _dict['buy_date']
        avg_price = _dict['avg_price']
        total_share = _dict['total_share']
        total_invest = _dict['total_invest']
        invest_times = _dict['invest_times']
        last_date_idx = _dict['last_date_idx']
        idx = current_stock_data[current_stock_data['trade_date'] == current_date].index.values[0]
        close = current_stock_data.ix[idx, 'close']
        high = current_stock_data.ix[idx, 'high']
        # weight = 2.0
        weight = 1 / np.log2(np.fmax(invest_times, 1) + 1) + 1
        sell_price = round(avg_price * weight, 2)

        if idx - last_date_idx >= invest_term_days and close < avg_price:
            share_cnt = math.modf(per_invest / (close * 100))[1]
            invest = share_cnt * 100 * close
            total_share += share_cnt
            total_invest += invest
            invest_times += 1
            avg_price = total_invest / (total_share * 100)
            in_stock_dict[code] = {'name': stock_name, 'invest_times': invest_times, 'total_share': total_share,
                                   'avg_price': avg_price, 'total_invest': total_invest, 'buy_date': buy_date,
                                   'last_date_idx': idx}
            # print(code, stock_name, 'buy', current_date, invest_times, close, share_cnt, invest, avg_price, total_share,
            #       total_invest, close / avg_price)

            return invest * -1
        elif high > sell_price:
            sell_share = math.modf(total_share / weight)[1] + 1
            total_share -= sell_share
            value = sell_share * 100 * sell_price
            rcd = {'name': stock_name, 'invest_times': invest_times, 'total_share': total_share,
                   'buy_date': buy_date, 'sell_date': current_date}
            out_stock_dict[code] = rcd
            in_stock_dict.pop(code)
            # print(code, stock_name, 'sell', current_date, sell_price, sell_share, value, total_share, weight)

            return value
        else:
            return 0
    else:
        return 0


while True:
    cash = 0
    total_money = 0
    in_stock_dict = {}  # {code:{name:'', invest_times:0, total_share:0, total_invest:0,buy_date:'',last_date_idx:''}}
    out_stock_dict = {}  # {code:{name:'', invest_times:0, total_share:0, buy_date:'', sell_date:''}}

    for hs_idx in hs300_data.index:
        if hs_idx % 23 == 0:
            cash += monthly_invest
            total_money += monthly_invest

        current_date = hs300_data.ix[hs_idx, 'trade_date']
        in_stock_ls = list(in_stock_dict.keys())
        for code in in_stock_ls:
            per_invest = np.fmin(cash, monthly_invest + int(cash * 0))
            money = trade_stock(current_date, code, in_stock_dict, out_stock_dict, per_invest)
            cash += money

        if len(in_stock_dict) < max_stock and cash >= monthly_invest:
            per_invest = np.fmin(cash, monthly_invest + int(cash * 0))
            invest = buy_new_stock(current_date, in_stock_dict, out_stock_dict, per_invest)
            cash -= invest
    else:
        value = 0
        invest = 0
        profit = 0
        for code, _dict in in_stock_dict.items():
            stock_data = data.get(code)
            invest += _dict['total_invest']
            total_share = _dict['total_share']
            close = stock_data.tail(1)['close'].values[0]
            value += close * total_share * 100

        for code, _dict in out_stock_dict.items():
            stock_data = data.get(code)
            total_share = _dict['total_share']
            close = stock_data.tail(1)['close'].values[0]
            profit += close * total_share * 100

        print(total_money, cash, invest, value, profit, value / invest, (cash + value + profit) / total_money)
        # print('*****************************************************')
