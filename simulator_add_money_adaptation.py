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
end_date = '20191231'

astocks = data_download().get_Astocks()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
stocks = stocks.merge(astocks, on=['code', 'name'])

hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30, 120])

data = {}
for i in stocks.index[:]:
    code = stocks.ix[i, 'code']
    stock_data = data_download().get_stock_day_data(code, ma_list=[5, 10, 20, 30, 120], start_date=start_date,
                                                    end_date=end_date)
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
    stock_code = ''
    money = 0
    max_stock = 3
    per_add = 100000
    total_invest = 0
    dingtou_days = 0
    per_invest = per_add
    invest_term_days = 70
    in_stock_dict = {}  # {code:{share_cnt:0,invest:0,buy_date:0}}
    dingtou_dict = {}  # {code:{invest_times:0, total_share:0,avg_price:0}}
    records = []

    for i in hs300_data.index:
        dingtou_days+=1
        if i % 22 == 0:
            money += per_add
            total_invest += per_add

        trade_date = hs300_data.ix[i, 'trade_date']
        hs300_close = hs300_data.ix[i, 'close']
        hs300_chg = hs300_data.ix[i, 'change']
        hs300_ma10 = hs300_data.ix[i, 'ma10']
        hs300_ma20 = hs300_data.ix[i, 'ma20']
        hs300_ma30 = hs300_data.ix[i, 'ma30']
        hs300_vol = hs300_data.ix[i, 'vol']
        hs300_ma_v_30 = hs300_data.ix[i, 'ma_v_30']
        hs300_ma_v_120 = hs300_data.ix[i, 'ma_v_120']

        # flag = hs300_ma_v_30 > hs300_ma_v_120
        flag = hs300_close > hs300_ma30 and hs300_ma_v_30 > hs300_ma_v_120
        # flag = hs300_close > hs300_ma30 and hs300_ma_v_30 > hs300_ma_v_120 and hs300_vol > hs300_ma_v_120
        # ma_status = trend().ma_up2(data=hs300_data, trade_date=trade_date, period=10, ma='ma_v_120')

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

        if len(dingtou_dict) > 0:
            stock_code = list(dingtou_dict.keys())[0]
            stock_data = data.get(stock_code)
            if trade_date not in stock_data['trade_date'].values:
                continue
            idx = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
            close = stock_data.ix[idx, 'close']
            high = stock_data.ix[idx, 'high']
            weight = 1.5
            # weight = 1 / np.log2(np.fmax(invest_times, 1) + 1) + 1
            avg_price = dingtou_dict.get(stock_code).get('avg_price')
            total_share = dingtou_dict.get(stock_code).get('total_share')
            invest_times = dingtou_dict.get(stock_code).get('invest_times')
            sell_price = round(avg_price * weight, 2)

            if dingtou_days % invest_term_days == 0 and close < avg_price:
                invest_weight = avg_price / close
                per_invest = per_invest * invest_weight
                if money <= per_invest:
                    per_invest = money
                share_cnt = math.modf(per_invest / (close * 100))[1]
                invest = share_cnt * 100 * close
                avg_price = (total_share * avg_price * 100 + invest) / (total_share * 100 + share_cnt * 100)
                total_share += share_cnt
                invest_times += 1
                money -= invest
                rcd = {'invest_times': invest_times, 'total_share': total_share, 'avg_price': avg_price}
                dingtou_dict[stock_code] = rcd
                # print('buy',stock_code, 'dingtou_days=',dingtou_days,invest_times, close, share_cnt, invest, avg_price, total_share, money)
            elif high > sell_price:
                dingtou_dict.pop(stock_code)
                value = total_share * 100 * sell_price * (1 - 0.002)
                money += value
                # print('sell',stock_code, 'dingtou_days=',dingtou_days, trade_date, weight, close, high,sell_price, total_share, value, money)

        if not flag and len(dingtou_dict) == 0:
            # per_invest = per_add
            per_invest = per_add + int(money * 0.1)
            stock_code = select_stock(trade_date)
            stock_data = data.get(stock_code)

            if stock_data is not None and trade_date in stock_data['trade_date'].values:
                current_idx = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
                if current_idx > invest_term_days:
                    close = stock_data.ix[current_idx, 'close']
                    share_cnt = math.modf(per_invest / (close * 100))[1]
                    if share_cnt > 0:
                        dingtou_days=0
                        invest = close * share_cnt * 100
                        money -= invest
                        rcd = {'invest_times': 1, 'total_share': share_cnt, 'avg_price': close}
                        dingtou_dict[stock_code] = rcd
                        # print('buy',stock_code, 'dingtou_days=',dingtou_days, trade_date, 1, close, share_cnt, invest, close, share_cnt, money)


        # elif hs300_close > hs300_ma30 and hs300_ma20>=hs300_ma30 and hs300_chg>0:
        elif flag and len(in_stock_dict) < max_stock:
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
                if pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol:
                    # if close > ma_20 and not bar_stop:
                    if key not in in_stock_dict:
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
                    # print(stock_code,in_stock_dict)

    else:
        if len(in_stock_dict) > 0:
            ls = list(in_stock_dict.keys())
            for stock_code in ls:
                stock_data = data.get(stock_code)
                if trade_date not in stock_data['trade_date'].values:
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

        for code, rcd in dingtou_dict.items():
            share_cnt = rcd['total_share']
            stock_data = data.get(code)
            money += stock_data.tail(1)['close'].values[0] * share_cnt * 100

    records = pd.DataFrame(records, columns=['code', 'buy_date', 'sell_date', 'days', 'buy_price', 'sell_price', 'rate',
                                             'money'])
    print('hs300', 'hs300_close > hs300_ma30 and hs300_ma_v_30 > hs300_ma_v_120', 'max_stock=', max_stock,
          start_date, end_date, len(records), records['rate'].min(), records['rate'].mean(), records['rate'].max(),
          money, total_invest, money / total_invest, True if money > total_invest else False)

    # if money / 1000000 > 15:
    #     print(records[['code', 'buy_date', 'sell_date', 'days', 'buy_price', 'sell_price', 'rate']])
