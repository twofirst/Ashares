import math
import pandas as pd
from data_download import data_download
from trade import trade

pd.set_option('display.max_columns', 99)
pd.set_option('display.max_rows', 999)
file = './Files/stock_period_statistics_20090101-20181231.csv'
start_date = '20090101'
end_date = '20181231'

astocks = data_download().get_Astocks()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
stocks = stocks.merge(astocks, on=['code', 'name'])

hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30, 120])

rcd=[]
data = {}
for i in stocks.index[:]:
    code = stocks.ix[i, 'code']

    # if code == '600372':
    #     continue

    stock_data = data_download().get_stock_day_data(code, ma_list=[5, 10, 20, 30, 120], start_date=start_date,
                                                    end_date=end_date)
    if stock_data is not None:
        data[code] = stock_data

bull = False
bull_list = []
vect = ['hs300_index']
columns=['code']
for i in hs300_data.index[3:]:
    trade_date = hs300_data.ix[i, 'trade_date']
    hs300_close = hs300_data.ix[i, 'close']
    hs300_ma30 = hs300_data.ix[i, 'ma30']
    hs300_ma_v_30_pre3 = hs300_data.ix[i - 3, 'ma_v_30']
    hs300_ma_v_30_pre2 = hs300_data.ix[i - 2, 'ma_v_30']
    hs300_ma_v_30_pre1 = hs300_data.ix[i - 1, 'ma_v_30']
    hs300_ma_v_30 = hs300_data.ix[i, 'ma_v_30']
    hs300_ma_v_120 = hs300_data.ix[i, 'ma_v_120']
    flag = hs300_close > hs300_ma30 and hs300_ma_v_30 > hs300_ma_v_120
    # and hs300_ma_v_30 > hs300_ma_v_30_pre1 and hs300_ma_v_30_pre1 > hs300_ma_v_30_pre2 and hs300_ma_v_30_pre2 > hs300_ma_v_30_pre3
    # print(trade_date, flag)

    if not bull and flag:
        bull = True
        bull_start = trade_date
        start_close=hs300_close
    elif bull and not flag:
        bull_end = trade_date
        bull = False
        bull_list.append((bull_start, bull_end))

        df = hs300_data[(hs300_data['trade_date'] >= bull_start) & (hs300_data['trade_date'] <= bull_end)]
        start_close = df['close'].values[0]
        end_close = df['close'].values[-1]
        max_close = df['close'].max()
        max_date=df[df['close']==max_close]['trade_date'].values[0]
        min_close=df[df['trade_date'] <= max_date]['close'].min()

        if start_close < max_close:
            rate = (max_close - min_close) / min_close
        else:
            rate = end_close / start_close - 1

        vect.append(rate)
        columns.append(bull_start+'_'+bull_end)


rcd.append(vect)
for stock_code in data.keys():
    vect=[stock_code]
    stock_data = data.get(stock_code)

    for start, end in bull_list:
        df = stock_data[(stock_data['trade_date'] >= start) & (stock_data['trade_date'] <= end)]
        if len(df)==0:
            vect.append(0)
            continue
        start_close = df['close'].values[0]
        end_close = df['close'].values[-1]
        max_close = df['close'].max()
        max_date=df[df['close']==max_close]['trade_date'].values[0]
        min_close=df[df['trade_date'] <= max_date]['close'].min()

        if start_close < max_close:
            rate = (max_close - min_close) / min_close
        else:
            rate = end_close / start_close - 1

        vect.append(rate)
    else:
        rcd.append(vect)


records = pd.DataFrame(rcd,columns=columns)
# records.to_csv(file)
