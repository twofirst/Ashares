import math
import pandas as pd
from data_download import data_download
from trade import trade

pd.set_option('display.max_columns', 99)
pd.set_option('display.max_rows', 999)
file = './Files/stock_rank_hs300_20090101-20181231.csv'
start_date = '20090101'
end_date = '20181231'

astocks = data_download().get_Astocks()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
stocks = stocks.merge(astocks, on=['code', 'name'])

hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30, 120])

data = {}
for i in stocks.index[:]:
    code = stocks.ix[i, 'code']

    if code == '600372':
        continue

    stock_data = data_download().get_stock_day_data(code, ma_list=[5, 10, 20, 30, 120], start_date=start_date,
                                                    end_date=end_date)
    if stock_data is not None:
        data[code] = stock_data

df = []
for stock_code in data.keys():
    stock_data = data.get(stock_code)
    money = 1000000
    in_stock_flag = False
    records = []

    for i in hs300_data.index:
        trade_date = hs300_data.ix[i, 'trade_date']
        hs300_close = hs300_data.ix[i, 'close']
        hs300_ma30 = hs300_data.ix[i, 'ma30']
        hs300_ma_v_30 = hs300_data.ix[i, 'ma_v_30']
        hs300_ma_v_120 = hs300_data.ix[i, 'ma_v_120']

        flag = hs300_close > hs300_ma30 and hs300_ma_v_30 > hs300_ma_v_120

        if flag and not in_stock_flag:
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
            if pre_close < pre_ma20 and close > ma_20 and not bar_stop and change > 0 and vol > pre_vol and close / ma_20 <= 1.05:
                share_cnt = math.modf(money / (close * 100))[1]

                if share_cnt > 0:
                    invest = close * 100 * share_cnt
                    money -= invest
                    in_stock_flag = True
                    buy_price = close
                    buy_date = trade_date

        elif in_stock_flag:
            if trade_date not in stock_data['trade_date'].values:
                continue
            stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
            close = stock_data.ix[stock_index, 'close']
            ma_20 = stock_data.ix[stock_index, 'ma20']

            if close <= ma_20:
                value = close * share_cnt * 100 * (1 - 0.002)
                earn = value - invest
                money += value
                rate = round(earn * 1.0 / invest, 2)
                invest = 0
                share_cnt = 0
                in_stock_flag=False
                record = [stock_code, buy_date, trade_date,
                          trade(None, None, None).calc_trade_days(buy_date, trade_date),
                          buy_price, close, rate, money]
                records.append(record)

    records = pd.DataFrame(records, columns=['code', 'buy_date', 'sell_date', 'days', 'buy_price', 'sell_price', 'rate',
                                             'money'])

    if len(records)>0:
        statistics = [stock_code, len(records), records['rate'].min(), records['rate'].mean(), records['rate'].max(),
                      sum(records['rate'] > 0) / len(records), (money + invest) * 1.0 / 1000000]
        print(statistics)
        df.append(statistics)

df = pd.DataFrame(df, columns=['code', 'trade_times', 'rate_min', 'rate_man', 'rate_max', 'success_rate', 'end_rate'])
df.to_csv(file, index=False)
