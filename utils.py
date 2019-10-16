import time
import datetime
import numpy as np


def calc_trade_days(buy_date, sell_date):
    date1 = time.strptime(str(buy_date), "%Y%m%d")
    date2 = time.strptime(str(sell_date), "%Y%m%d")
    d1 = datetime.date(date1[0], date1[1], date1[2])
    d2 = datetime.date(date2[0], date2[1], date2[2])
    days = (d2 - d1).days

    return days

def generate_comparison_feature(df, feature_ls):
    feature_name = str(feature_ls)
    df[feature_name] = True
    for i in np.arange(1, len(feature_ls)):
        df[feature_name] = df[feature_name] & (df[feature_ls[i]] > df[feature_ls[i - 1]])


def generate_sell_feature(df):
    df['close<ma10'] = df['close'] < df['ma10']
    df['close<ma20'] = df['close'] < df['ma20']
    df['close<ma30'] = df['close'] < df['ma30']
    df['close<ma10_or_ma20'] = df['close<ma10'] | df['close<ma20']
    df['close<ma10_and_ma20'] = df['close<ma10'] & df['close<ma20']
    df['close<ma20_or_ma30'] = df['close<ma20'] | df['close<ma30']
    df['close<ma20_and_ma30'] = df['close<ma20'] & df['close<ma30']
    df['increase_rate'] = df['close'] / df['pre_close']


def generate_features(df, ma_ls=['close', 'ma10', 'ma20', 'ma30'], vol_ls=['vol', 'ma_v_30', 'ma_v_120']):
    generate_sell_feature(df)

    for index_close_condition in itertools.permutations(ma_ls):
        generate_comparison_feature(df, index_close_condition)

    for index_vol_condition in itertools.permutations(vol_ls):
        generate_comparison_feature(df, index_vol_condition)
