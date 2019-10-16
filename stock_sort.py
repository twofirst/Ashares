import time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data_download import data_download
import urllib

# pd.set_option('display.max_columns', 99)
# pd.set_option('display.max_rows', 99)

ma_20 = 20
ma_30 = 30
show_num = 60
core_ma = 'ma20'
start_date = '20180101'
end_date = '20290310'
astocks = data_download().get_Astocks()
sz50_stocks = data_download().get_sz50()
stocks = data_download().get_hs300()[['code']]
# stocks = data_download().get_zz500()
stocks = stocks.merge(astocks, on=['code'])

hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30, 120])
hs300_close = hs300_data.loc[len(hs300_data) - 1, 'close']
hs300_ma30 = hs300_data.loc[len(hs300_data) - 1, 'ma30']
hs300_ma_v_30 = hs300_data.loc[len(hs300_data) - 1, 'ma_v_30']
hs300_ma_v_120 = hs300_data.loc[len(hs300_data) - 1, 'ma_v_120']
index_flag = hs300_close > hs300_ma30 and hs300_ma_v_30 > hs300_ma_v_120


def get_label(row):
    if row['close'] > row['ma20']:
        return 1
    else:
        return 0


df = hs300_data[['trade_date']]
a50_df = hs300_data[['trade_date']]
for i in stocks.index[:]:
    code = stocks.ix[i, 'code']
    stock_data = data_download().load_stock_day_data(code, start_date, end_date)
    if len(stock_data) > 0:
        stock_data['label'] = stock_data.apply(get_label, axis=1)
        stock_data = stock_data[['trade_date', 'label']]
        df = df.merge(stock_data, on='trade_date', how='outer')
        if code in sz50_stocks['code'].values:
            a50_df = a50_df.merge(stock_data, on='trade_date', how='outer')

a50_df['mean'] = a50_df.mean(axis=1)
hs300_data['mean'] = df.mean(axis=1)
a50_rate_ls = list(a50_df['mean'].values)[(len(a50_df) - show_num):]
hs300_rate_ls = list(hs300_data['mean'].values)[(len(a50_df) - show_num):]
hs300_point_ls = list(hs300_data['close'].values)[(len(a50_df) - show_num):]
record_time_ls = list(hs300_data['trade_date'])[(len(a50_df) - show_num):]

data = {}
rcd = []
for i in stocks.index[:]:
    code = stocks.loc[i, 'code']
    stock_data = data_download().get_stock_day_data(code, ma_list=[5, 10, 20, 30, 60, 90, 120],
                                                    start_date=start_date, end_date=end_date)

    if stock_data is not None and len(stock_data) > 0:
        name = stocks[stocks['code'] == code]['name'].values[0]
        pre_close = stock_data.tail(1)['close'].values[0]
        pre_ma_20 = stock_data.tail(1)['ma' + str(ma_20)].values[0]
        pre_ma_30 = stock_data.tail(1)['ma' + str(ma_30)].values[0]
        pre_vol = stock_data.tail(1)['vol'].values[0] * 100
        pre_vol_30 = stock_data.tail(1)['ma_v_30'].values[0] * 100
        pre_vol_120 = stock_data.tail(1)['ma_v_120'].values[0] * 100
        ma_20_sum = stock_data.tail(ma_20 - 1)['close'].sum()
        ma_30_sum = stock_data.tail(ma_30 - 1)['close'].sum()
        rcd.append(
            [code, name, pre_close, pre_vol, pre_vol_30, pre_vol_120, pre_ma_20, ma_20_sum, pre_ma_30, ma_30_sum])

rcd = pd.DataFrame(rcd,
                   columns=['code', 'name', 'pre_close', 'pre_vol', 'pre_vol_30', 'pre_vol_120', 'pre_ma_20',
                            'ma_20_sum', 'pre_ma_30', 'ma_30_sum'])


def get_time_rate():
    dt1 = datetime.datetime.now()
    dt2 = datetime.datetime(dt1.year, dt1.month, dt1.day, 9, 30, 0)
    minutes = (dt1 - dt2).seconds / 60
    if minutes > 120 and minutes <= 210:
        minutes = 120
    elif minutes > 210:
        minutes = min(minutes - 90, 240)

    return 240 / minutes


def get_real_data(code):
    real_data = data_download().get_stock_real_data(code)
    price = round(float(real_data['price'].values[0]), 2)
    vol = int(real_data['volume'].values[0]) * get_time_rate()

    return pd.Series([price, vol], dtype=np.float32)


def sort_features(data, ls, trade_date):
    dict_ = {}
    row = data[data['trade_date'] == trade_date]
    for item in ls:
        dict_[item] = row[item].values[0]
    sorted_pair = sorted(dict_.items(), key=lambda item: item[1])
    sorted_key = [pair[0] for pair in sorted_pair]
    features = str(sorted_key).replace('[', '(').replace(']', ')')

    return features


while True:
    rcd[['price', 'vol']] = rcd['code'].apply(lambda code: get_real_data(code))
    rcd['ma20'] = round((rcd['price'] + rcd['ma_20_sum']) / ma_20, 3)
    rcd['ma30'] = round((rcd['price'] + rcd['ma_30_sum']) / ma_30, 3)
    rcd['rate'] = round(rcd['price'] / rcd['pre_close'], 3)
    rcd['ma_rate'] = round(rcd['price'] / rcd['ma20'], 3)
    rcd['label'] = rcd['price'] > rcd[core_ma]
    hs300_label_mean = rcd['label'].mean()
    a50_rcd = rcd.merge(sz50_stocks, on='code')
    a50_label_mean = a50_rcd['label'].mean()

    # candidates_0 = rcd[
    #     (rcd['pre_close'] < rcd['pre_ma_30']) & (rcd['ma30'] < rcd['ma20']) & (rcd['ma20'] < rcd['price']) & (
    #             (rcd['pre_vol_120'] < rcd['pre_vol_30']) & (rcd['pre_vol_30'] < rcd['vol']))]
    #
    # candidates_1 = rcd[
    #     (rcd['pre_close'] < rcd['pre_ma_30']) & (rcd['ma20'] < rcd['ma30']) & (rcd['ma30'] < rcd['price']) & (
    #             (rcd['pre_vol_30'] < rcd['pre_vol_120']) & (rcd['pre_vol_120'] < rcd['vol']))]
    #
    # candidates_2 = rcd[
    #     (rcd['pre_close'] < rcd['pre_ma_30']) & (rcd['ma20'] < rcd['ma30']) & (rcd['ma30'] < rcd['price']) & (
    #             (rcd['pre_vol_30'] < rcd['vol']) & (rcd['vol'] < rcd['pre_vol_120']))]
    #
    # candidates_3 = rcd[
    #     (rcd['pre_close'] < rcd['pre_ma_20']) & (rcd['ma30'] < rcd['ma20']) & (rcd['ma20'] < rcd['price']) & (
    #             (rcd['vol'] < rcd['pre_vol_30']) & (rcd['pre_vol_30'] < rcd['pre_vol_120']))]
    #
    # print(candidates_0.sort_values(by='ma_rate')[['code', 'name', 'price', 'ma20', 'ma30', 'rate', 'ma_rate']])
    # print('--------------------------------------------------')
    # print(candidates_1.sort_values(by='ma_rate')[['code', 'name', 'price', 'ma20', 'ma30', 'rate', 'ma_rate']])
    # print('--------------------------------------------------')
    # print(candidates_2.sort_values(by='ma_rate')[['code', 'name', 'price', 'ma20', 'ma30', 'rate', 'ma_rate']])
    # print('--------------------------------------------------')
    # print(candidates_3.sort_values(by='ma_rate')[['code', 'name', 'price', 'ma20', 'ma30', 'rate', 'ma_rate']])
    # print('--------------------------------------------------')
    now = datetime.datetime.now()
    print(now, 'hs300 index flag:', index_flag, ' a50 up ma rate:', a50_label_mean, ' hs300 up ma rate:',
          hs300_label_mean)
    print('**************************************************************')

    hour = datetime.datetime.now().hour
    minute = datetime.datetime.now().minute
    t = hour * 100 + minute
    # if ( hour>= 9 and datetime.datetime.now().hour <= 15 and datetime.datetime.now().hour != 12) and not (
    #         datetime.datetime.now().hour == 11 and datetime.datetime.now().minute > 30):
    if (t >= 925 and t <= 1130) or (t >= 1300 and t <= 1505):
        a50_rate_ls.append(a50_label_mean)
        hs300_rate_ls.append(hs300_label_mean)
        record_time_ls.append('-'.join([str(now.hour), str(now.minute)]))
        resource = urllib.request.urlopen("http://hq.sinajs.cn/list=sh000300")
        content = resource.read().decode(resource.headers.get_content_charset())
        contents = str(content).split(',')
        hs300_point_ls.append(float(contents[3]))

        fig, ax1 = plt.subplots()
        ax1.plot(record_time_ls, a50_rate_ls, 'r-')
        ax1.plot(record_time_ls, hs300_rate_ls, 'b-')
        plt.xticks(record_time_ls, rotation=90)
        ax2 = ax1.twinx()  # mirror the ax1
        ax2.plot(record_time_ls, hs300_point_ls, 'k-')
        plt.savefig('PNG/stock_sort.png')
        plt.close()

    time.sleep(300)
