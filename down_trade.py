import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data_download import data_download

data = {}
down_times = 4
start_date = '20090101'
end_date = '20181231'
money = 1000000
max_stock = 2
in_stock_dict = {}  # {code:{share_cnt:0,invest:0,buy_date:0}}
records = []

hs300_stocks = data_download().get_hs300()
hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30, 120])

for i in hs300_stocks.index[:]:
    code = hs300_stocks.ix[i, 'code']
    stock_data = data_download().load_stock_day_data(code, start_date, end_date)
    data[code] = stock_data

for hs300_idx in hs300_data.index[:]:
    trade_date = hs300_data.ix[hs300_idx, 'trade_date']
    candidates = []

    if len(in_stock_dict) > 0:
        ls = list(in_stock_dict.keys())
        for stock_code in ls:
            stock_data = data.get(stock_code)
            if trade_date in stock_data['trade_date'].values:
                stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
                stock_close = stock_data.ix[stock_index, 'close']
                stock_high = stock_data.ix[stock_index, 'high']
                buy_price = in_stock_dict.get(stock_code).get('buy_price')
                buy_date = in_stock_dict.get(stock_code).get('buy_date')
                # if stock_close >= buy_price * 1.02:
                #     selll_price = buy_price * 1.02
                # else:
                selll_price = stock_close
                value = selll_price * in_stock_dict.get(stock_code).get('share_cnt') * 100 * (1 - 0.002)
                invest = in_stock_dict.get(stock_code).get('invest')
                earn = value - invest
                money += value
                rate = round(earn / invest, 2)

                record = [stock_code, buy_date, trade_date, buy_price, selll_price, invest, value, rate, money]
                print(record)
                records.append(record)
                in_stock_dict.pop(stock_code)

    for code, stock_data in data.items():
        if trade_date in stock_data['trade_date'].values:
            stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
            if stock_index >= down_times:
                min_close = stock_data.ix[stock_index, 'close']
                # close_ls = [min_close]

                for i in np.arange(1, down_times):
                    if stock_data.ix[stock_index - i, 'low'] > min_close:
                        min_close = stock_data.ix[stock_index - i, 'close']
                        # close_ls.append(min_close)
                    else:
                        break
                else:
                    candidates.append(code)
    else:
        if len(candidates) > 0 and len(in_stock_dict) < max_stock:
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
                    # print(trade_date,close,share_cnt,invest,valid_money,money)
                    money -= invest
                    buy_date = trade_date
                    in_stock_dict[stock_code] = {'share_cnt': share_cnt, 'invest': invest, 'buy_date': buy_date,
                                                 'buy_price': close}
