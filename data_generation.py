import math
import numpy as np
import pandas as pd
from data_download import data_download


# pd.set_option('display.max_columns', 99)
# pd.set_option('display.max_rows', 999)


def whether_buy_condition(stock_data, idx, core_ma):
    close = stock_data.ix[idx, 'close']
    ma = stock_data.ix[idx, core_ma]
    pre_close = stock_data.ix[idx - 1, 'close']
    pre_ma = stock_data.ix[idx - 1, core_ma]
    pct_chg = stock_data.ix[idx, 'pct_chg']

    vol= stock_data.ix[idx, 'vol']
    vol30= stock_data.ix[idx, 'ma_v_30']
    vol120= stock_data.ix[idx, 'ma_v_120']
    if close > ma and pre_close <= pre_ma and pct_chg >= 0 and pct_chg <= 1.05 and vol>vol30 and vol30>vol120:
    # if close > ma and pre_close <= pre_ma and pct_chg >= 0 and pct_chg <= 1.05:
        return True
    else:
        return False


def whether_sell_condition(stock_data, idx, core_ma):
    close = stock_data.ix[idx, 'close']
    ma = stock_data.ix[idx, core_ma]
    pre_close = stock_data.ix[idx - 1, 'close']
    pre_ma = stock_data.ix[idx - 1, core_ma]

    if close < ma and pre_close >= pre_ma:
        return True
    else:
        return False


def get_ma_sort(stock_data, idx, ma_ls):
    feature_dict = {'close': 'm1', 'ma5': 'm5', 'ma10': 'm10', 'ma20': 'm20', 'ma30': 'm30', 'vol': 'v1',
                    'ma_v_30': 'v30',
                    'ma_v_120': 'v120'}
    dict_ = {}
    for ma in ma_ls:
        dict_[ma] = stock_data.ix[idx, ma]
    sorted_pairs = sorted(dict_.items(), key=lambda item: item[1])
    sorted_keys = [feature_dict.get(pair[0]) for pair in sorted_pairs]
    combined_feature = '-'.join(sorted_keys)

    return combined_feature


def get_feature_trend(stock_data, stock_idx, feature):
    dict_ = {'d1': stock_data.ix[stock_idx, feature], 'd2': stock_data.ix[stock_idx - 1, feature],
             'd3': stock_data.ix[stock_idx - 2, feature]}
    sorted_pairs = sorted(dict_.items(), key=lambda item: item[1])
    sorted_keys = [pair[0] for pair in sorted_pairs]
    combined_feature = '-'.join(sorted_keys)

    return combined_feature


def generate_features(index_data, stock_data, buy_date):
    features = []
    for data in [index_data, stock_data]:
        idx = data[data['trade_date'] == buy_date].index.values[0]
        # three days
        for offset in [0, 1, 2]:
            features.append(data.ix[idx - offset, 'vol'] / data.ix[idx - offset - 1, 'vol'])
            features.append(data.ix[idx - offset, 'close'] / data.ix[idx - offset - 1, 'close'])
            features.append(get_ma_sort(data, idx - offset, ['vol', 'ma_v_30', 'ma_v_120']))
            features.append(get_ma_sort(data, idx - offset, ['close', 'ma5', 'ma10', 'ma20', 'ma30']))
            for ma in ['ma5', 'ma10', 'ma20', 'ma30']:
                features.append(get_feature_trend(data, idx - offset, ma))
                features.append(data.ix[idx - offset, 'close'] / data.ix[idx - offset, ma])
            for v in ['ma_v_30', 'ma_v_120']:
                features.append(get_feature_trend(data, idx - offset, v))
                features.append(data.ix[idx - offset, 'vol'] / data.ix[idx - offset, v])

    return features


if __name__ == '__main__':
    file = './Files/data_generation_core_buy20_sell20_vol_30_120_index_bull_20160101-20181231.csv'
    start_date = '20160101'
    end_date = '20181231'
    stocks = data_download().get_hs300()
    index_data = data_download().get_hs300_index(start_date, end_date, ma=[5, 10, 20, 30, 120])
    record_ls = []

    for core_buy_ma in ['ma20']:
        for core_sell_ma in ['ma20']:
            for i in stocks.index[:]:
                code = stocks.ix[i, 'code']
                stock_data = data_download().load_stock_day_data(code, start_date=start_date, end_date=end_date)
                in_stock = False
                buy_price = 0
                buy_date = ''
                min_close = 0
                max_close = 0
                max_down_rate = 0
                inter_down_rate = 0
                features = []

                for stock_idx in stock_data.index[4:]:
                    trade_date = stock_data.ix[stock_idx, 'trade_date']
                    index_idx = index_data[index_data['trade_date'] == trade_date].index.values[0]

                    if not in_stock and whether_buy_condition(stock_data, stock_idx, core_buy_ma) and stock_data.ix[
                        stock_idx, 'close'] > stock_data.ix[stock_idx, core_sell_ma]:
                        if index_data.ix[index_idx, 'close'] <= index_data.ix[index_idx, core_buy_ma] or index_data.ix[
                            index_idx, 'vol'] <= index_data.ix[index_idx, 'ma_v_30'] or index_data.ix[
                            index_idx, 'ma_v_30'] <= index_data.ix[index_idx, 'ma_v_120']:
                            continue

                        in_stock = True
                        buy_price = stock_data.ix[stock_idx, 'close']
                        min_close = buy_price
                        max_close = buy_price
                        max_down_rate = 0
                        inter_down_rate = 0
                        buy_date = stock_data.ix[stock_idx, 'trade_date']
                        features = generate_features(index_data, stock_data, buy_date)
                    elif in_stock:
                        close = stock_data.ix[stock_idx, 'close']
                        min_close = close if close < min_close else min_close
                        if close > max_close:
                            max_close = close
                            inter_down_rate = max_down_rate
                        down_rate = (max_close - close) / max_close
                        max_down_rate = down_rate if down_rate > max_down_rate else max_down_rate
                        if whether_sell_condition(stock_data, stock_idx, core_sell_ma):
                            sell_price = stock_data.ix[stock_idx, 'close']
                            sell_date = stock_data.ix[stock_idx, 'trade_date']
                            final_rate = sell_price * (1 - 0.002) / buy_price
                            label = True if final_rate > 1 else False
                            features.extend([core_buy_ma, core_sell_ma, label, code, buy_date, buy_price, min_close,
                                             min_close / buy_price - 1, max_close, max_close / buy_price,
                                             inter_down_rate,
                                             sell_date, sell_price, final_rate])
                            record_ls.append(features.copy())
                            in_stock = False
                            features.clear()

    record = pd.DataFrame(record_ls)
    record.to_csv(file, index=False)
    print(len(record))
