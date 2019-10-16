import math
import time
import datetime
import numpy as np
import pandas as pd
import tushare as ts
from trend import trend

pd.set_option('display.max_columns', 99)
pd.set_option('display.max_rows', 999)

pro = ts.pro_api('d334f1680cb3c7416c20531cd836c7d8552df45a5a808e410d9e74c4')
# stocks=pro.hs_const(hs_type='SH')
# stocks = ts.get_sz50s()
stocks = ts.get_hs300s()
Astocks = pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')

results = []
start_date = 20100101
end_date = 20151231

for code in stocks['code']:
    # for code in Astocks['ts_code']:
    # code = '600776'
    try:
        if '.' not in code:
            if code[0] == '6':
                code = code + '.SH'
            else:
                code = code + '.SZ'
        stock_idx = Astocks[Astocks['ts_code'] == code].index[0]
        name = Astocks.ix[stock_idx, 'name']
        industry = Astocks.ix[stock_idx, 'industry']
        df = ts.pro_bar(pro_api=pro, ts_code=code, start_date='20010101', end_date='20181221',
                        adj='qfq', ma=[5, 10, 20, 25, 30, 40, 50, 60, 80, 90, 100, 120, 150])
        df['trade_date'] = df['trade_date'].apply(lambda x: int(x))
        df.sort_index(ascending=True, inplace=True)
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        target = df[(df['trade_date'] >= start_date) & (df['trade_date'] <= end_date)]

        for ma1 in [30]:
            buy_ma = 'ma' + str(ma1)
            for ma2 in [30]:
                sell_ma = 'ma' + str(ma2)
                if ma2 > ma1:
                    continue

                trades = []
                share_cnt = 0
                money = 100000
                stock_value = 0
                bull_market = False
                in_stock_flag = False

                for i in target.index[1:]:
                    row = target.ix[i, :]
                    last_row = target.ix[i - 1, :]
                    trade_date = str(row['trade_date'])

                    # if not in_stock_flag and last_row['close'] < last_row[buy_ma] and row['close'] > row[buy_ma] and \
                    #         row['vol'] > row['ma_v_120']:
                    if not in_stock_flag and row['close'] > row[buy_ma]:
                        stock_value = money
                        share_cnt = math.modf(money / (row['close'] * 100))[1]
                        if share_cnt > 0:
                            buy_price = row['close']
                            money = money - row['close'] * 100 * share_cnt
                            in_stock_flag = True
                    elif in_stock_flag and row['close'] < row[sell_ma]:
                        money = money + row['close'] * 100 * share_cnt * (1 - 0.002)
                        share_cnt = 0
                        in_stock_flag = False
                        date1 = time.strptime(str(trade_date), "%Y%m%d")
                        date2 = time.strptime(str(row['trade_date']), "%Y%m%d")
                        d1 = datetime.date(date1[0], date1[1], date1[2])
                        d2 = datetime.date(date2[0], date2[1], date2[2])
                        days = (d2 - d1).days
                        trades.append(
                            [trade_date, row['trade_date'], days, round((money - stock_value) / stock_value, 2), money])

                if share_cnt > 0:
                    money = money + row['close'] * 100 * share_cnt * (1 - 0.002)
                    share_cnt = 0
                    trades.append(
                        [trade_date, row['trade_date'], 'still', round((money - stock_value) / stock_value, 2), money])
                trades = pd.DataFrame(trades,
                                      columns=['buy_date', 'sell_date', 'days', 'rate', 'money'])
                if len(trades) > 0:
                    final_ratio = round((money - 100000) / 100000, 2)
                    r = [code, name, industry, buy_ma, sell_ma, len(trades),
                         final_ratio, min(trades['rate']), max(trades['rate'])]
                    results.append(r)
                    print(r, True if final_ratio > 0 else False)
                    # trades.sort_values(by='rate', ascending=True, inplace=True)
                    # print(trades)
                    # print(results)
                    temp = pd.DataFrame(results,
                                        columns=['code', 'name', 'industry', 'buy_ma', 'sell_ma', 'trade_times',
                                                 'ratio', 'min', 'max'])
                    temp.to_csv('./Files/ma_trade_all_v120_20181016-20181231.csv', index=False)
    except:
        print('error')
        continue
        # print(buy_ma, sell_ma, temp['ratio'].mean(), temp['ratio'].min(), temp['ratio'].max(), temp['min'].min(),
        #       temp['max'].max(), temp['trade_times'].min(), temp['trade_times'].mean(),
        #       temp['trade_times'].max())
    # break

print(temp['ratio'].min(), temp['ratio'].mean(), temp['ratio'].max())
print(start_date,end_date)