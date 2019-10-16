import os
import math
import pickle
import numpy as np
import pandas as pd
from data_download import data_download
from trade import trade
from models import *

pd.set_option('display.max_columns', 999)
pd.set_option('display.max_rows', 999)
base_path = '/home/twofirst/Documents/Astock/grid_simulator/'
compare_file = base_path + 'compare_results.csv'
compare_records = []
start_date = '20090101'
end_date = '20181231'
loop_num = 2000

astocks = data_download().get_Astocks()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
# stocks=astocks
stocks = stocks.merge(astocks, on=['code', 'name'])
index_data = data_download().get_hs300_index(start_date, end_date, ma=[5, 10, 20, 30, 120])
hs300_class = pd.read_table('HS300_class.txt', header=0, dtype='str')


def compare_value(df):
    df['close_None'] = True
    df['close>ma10'] = df['close'] > df['ma10']
    df['close>ma20'] = df['close'] > df['ma20']
    df['close>ma30'] = df['close'] > df['ma30']
    df['close>ma20_or_ma30'] = (df['close'] > df['ma20']) | (df['close'] > df['ma30'])
    df['close>ma20_and_ma30'] = (df['close'] > df['ma20']) & (df['close'] > df['ma30'])
    df['increase_rate'] = df['close'] / df['pre_close']

    df['vol_None'] = True
    df['vol>vol30'] = df['vol'] > df['ma_v_30']
    df['vol>vol120'] = df['vol'] > df['ma_v_120']
    df['vol>vol30_or_vol120'] = (df['vol'] > df['ma_v_30']) | (df['vol'] > df['ma_v_120'])
    df['vol>vol30_and_vol120'] = (df['vol'] > df['ma_v_30']) & (df['vol'] > df['ma_v_120'])
    df['vol>vol30_vol30>vol120'] = (df['vol'] > df['ma_v_30']) & (df['ma_v_30'] > df['ma_v_120'])

    return df


def build_trade_dict(index_data, data, index_close_condition, index_vol_condition, buy_vol_condition,
                     buy_close_condition, sell_condition, increase_rate):
    trade_dict = {}
    for code, stock_data in data.items():
        instock_flag = False
        record = []
        buy_date, sell_date, buy_price, sell_price, rate = None, None, None, None, None
        for idx in stock_data.index[1:]:
            trade_date = stock_data.ix[idx, 'trade_date']
            index_idx = index_data[index_data['trade_date'] == trade_date].index.values[0]
            index_flag = index_data.ix[index_idx, index_close_condition] & index_data.ix[index_idx, index_vol_condition]
            if not instock_flag and not index_flag:
                continue

            if not instock_flag:
                pre_close_condition_boolean = stock_data.ix[idx - 1, buy_close_condition]
                buy_close_condition_boolean = stock_data.ix[idx, buy_close_condition]
                buy_vol_condition_boolean = stock_data.ix[idx - 1, buy_vol_condition]

                if not pre_close_condition_boolean and buy_close_condition_boolean and buy_vol_condition_boolean and \
                        stock_data.ix[idx, 'increase_rate'] <= increase_rate:
                    buy_date = trade_date
                    buy_price = stock_data.ix[idx, 'close']
                    instock_flag = True
            else:
                pre_sell_condition_boolean = stock_data.ix[idx - 1, sell_condition]
                sell_condition_boolean = stock_data.ix[idx, sell_condition]
                if (pre_sell_condition_boolean and not sell_condition_boolean) or (idx == len(stock_data) - 1):
                    sell_date = trade_date
                    sell_price = stock_data.ix[idx, 'close']
                    instock_flag = False
                    rate = sell_price * (1 - 0.002) / buy_price
                    record.append([code, buy_date, buy_price, sell_date, sell_price, rate,
                                   True if rate > 1 else False])
                    dict_ = {'code': code, 'buy_date': buy_date, 'sell_date': sell_date,
                             'buy_price': buy_price, 'sell_price': sell_price, 'rate': rate,
                             'success': True if rate > 1 else False}
                    if buy_date not in trade_dict:
                        trade_dict[buy_date] = [dict_]
                    else:
                        dicts = trade_dict[buy_date]
                        dicts.append(dict_)

    return trade_dict


def trade_stock(index_data, trade_dict, class_stock_ls, position):
    money = 1000000
    in_stock_dict = {}
    sell_date_dict = {}
    one_loop_record = []
    for trade_date in index_data['trade_date']:
        # sell first
        if trade_date in sell_date_dict:
            sell_code_ls = sell_date_dict[trade_date]
            sell_date_dict.pop(trade_date)
            for code in sell_code_ls:
                dict_ = in_stock_dict.get(code)
                buy_date = dict_.get('buy_date')
                sell_date = dict_.get('sell_date')
                buy_price = dict_.get('buy_price')
                sell_price = dict_.get('sell_price')
                success = dict_.get('success')
                share_cnt = dict_.get('share_cnt')
                invest = dict_.get('invest')
                value = sell_price * share_cnt * 100 * (1 - 0.002)
                earn = value - invest
                money += value
                rate = round(earn / invest, 2)
                one_loop_record.append(
                    [code, buy_date, buy_price, share_cnt, invest, sell_date,
                     sell_price, rate, success, money])
                in_stock_dict.pop(code)

        # buy
        if len(in_stock_dict) < max_stock and trade_date in trade_dict.keys():
            candidates = []
            for d in trade_dict.get(trade_date):
                if d['code'] in class_stock_ls:
                    candidates.append(d)
            target_num = min(len(candidates), max_stock - len(in_stock_dict))
            if target_num > 0:
                if position == 'full':
                    valid_money = money / target_num
                else:
                    valid_money = money / (max_stock - len(in_stock_dict))

                while target_num > 0:
                    ranint = np.random.randint(len(candidates))
                    dict_ = candidates[ranint]
                    candidates.pop(ranint)
                    target_num -= 1

                    buy_price = dict_.get('buy_price')
                    share_cnt = math.modf(valid_money / (buy_price * 100))[1]
                    if share_cnt > 0:
                        invest = buy_price * 100 * share_cnt
                        dict_['share_cnt'] = share_cnt
                        dict_['invest'] = invest
                        money -= invest

                        code = dict_.get('code')
                        sell_date = dict_.get('sell_date')
                        in_stock_dict[code] = dict_
                        if sell_date in sell_date_dict:
                            sell_date_dict[sell_date].append(code)
                        else:
                            sell_date_dict[sell_date] = [code]

    return one_loop_record, money


index_data = compare_value(index_data)

data = {}
for i in stocks.index[:]:
    code = stocks.ix[i, 'code']
    # if code != '600018':
    #     continue

    stock_data = data_download().load_stock_day_data(code, start_date=start_date, end_date=end_date)
    if stock_data is not None:
        data[code] = compare_value(stock_data)

for index_close_condition in ['close>ma20', 'close>ma30']:  # 'close>ma10', 'close_None'
    for index_vol_condition in ['vol>vol30', 'vol>vol120', 'vol>vol30_or_vol120', 'vol>vol30_and_vol120',
                                'vol>vol30_vol30>vol120', 'vol_None']:
        for buy_vol_condition in ['vol>vol30', 'vol>vol120', 'vol>vol30_or_vol120', 'vol>vol30_and_vol120',
                                  'vol>vol30_vol30>vol120', 'vol_None']:
            for buy_close_condition in ['close>ma20', 'close>ma30', 'close>ma20_or_ma30', 'close>ma20_and_ma30']:
                for sell_condition in ['close>ma20', 'close>ma30', 'close>ma20_or_ma30', 'close>ma20_and_ma30']:
                    if buy_close_condition != 'close>ma20_and_ma30' and sell_condition != 'close>ma20_and_ma30' and buy_close_condition != sell_condition:
                        continue
                    elif buy_close_condition == 'close>ma20_or_ma30' and sell_condition == 'close>ma20_or_ma30':
                        continue

                    for increase_rate in np.arange(1.02, 1.08, 0.02):

                        trade_dict = build_trade_dict(index_data, data, index_close_condition, index_vol_condition,
                                                      buy_vol_condition, buy_close_condition,
                                                      sell_condition, increase_rate)
                        for stock_class in ['Other', 'Period', 'Financial', 'Other_Financial', 'All']:
                            if stock_class == 'All':
                                class_stock_ls = hs300_class['code'].values.tolist()
                            elif stock_class == 'Other_Financial':
                                class_stock_ls = hs300_class[hs300_class['class'] == 'Other']['code'].values.tolist()
                                financial_ls = hs300_class[hs300_class['class'] == 'Financial']['code'].values.tolist()
                                class_stock_ls.extend(financial_ls)
                            else:
                                class_stock_ls = hs300_class[hs300_class['class'] == stock_class][
                                    'code'].values.tolist()

                            for max_stock in np.arange(1, 6):
                                for position in ['full', 'less']:
                                    if max_stock == 1 and position == 'less':
                                        continue
                                    all_records = []
                                    for num in np.arange(loop_num):
                                        one_loop_record, money = trade_stock(index_data, trade_dict, class_stock_ls,
                                                                             position)

                                        one_loop_record = pd.DataFrame(one_loop_record,
                                                                       columns=['code', 'buy_date', 'buy_price',
                                                                                'share_cnt', 'invest', 'sell_date',
                                                                                'sell_price', 'rate', 'success',
                                                                                'money'])
                                        trade_times = len(one_loop_record)
                                        earn_rate = round(money / 1000000 - 1, 2)
                                        success_rate = round(one_loop_record['success'].mean(), 3)
                                        all_records.append([trade_times, earn_rate, success_rate])
                                        record_name = str(num) + '_' + str(trade_times) + '_' + str(
                                            earn_rate) + '_' + str(
                                            success_rate)

                                    file_name = base_path + 'records/' + index_close_condition + '-' + index_vol_condition + '-' + buy_close_condition + '-' + buy_vol_condition + '-' + sell_condition + '-' + str(
                                        increase_rate) + '-' + stock_class + '-' + str(
                                        max_stock) + '-' + position + '.csv'
                                    all_records = pd.DataFrame(all_records,
                                                               columns=['trade_times', 'earn_rate', 'success_rate'])
                                    all_records.to_csv(file_name, index=False)
                                    statistics = [index_close_condition, index_vol_condition, buy_vol_condition,
                                                  buy_close_condition, sell_condition, increase_rate, stock_class,
                                                  max_stock, position,
                                                  all_records['earn_rate'].min(), all_records['earn_rate'].mean(),
                                                  all_records['earn_rate'].max(),
                                                  round(all_records['earn_rate'].std(), 2),
                                                  all_records['trade_times'].min(), all_records['trade_times'].mean(),
                                                  all_records['trade_times'].max(), all_records['success_rate'].min(),
                                                  all_records['success_rate'].mean(), all_records['success_rate'].max()]
                                    print(statistics)
                                    compare_records.append(statistics)
                                    df = pd.DataFrame(compare_records,
                                                      columns=['index_close_condition', 'index_vol_condition',
                                                               'buy_vol_condition', 'buy_close_condition',
                                                               'sell_condition', 'increase_rate', 'stock_class',
                                                               'max_stock', 'position', 'earn_rate_min',
                                                               'earn_rate_mean', 'earn_rate_max', 'earn_rate_std',
                                                               'trade_times_min', 'trade_times_mean', 'trade_times_max',
                                                               'success_rate_min', 'success_rate_mean',
                                                               'success_rate_max'])
                                    df.to_csv(compare_file, index=False)

    print(compare_records)
