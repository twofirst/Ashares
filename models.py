import numpy as np
import pandas as pd
from trend import trend
from xgboost import XGBClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score



def record_info(day_data, week_data, hs300_data,day_index):
    trade_date = day_data.ix[day_index, 'trade_date']
    close = day_data.ix[day_index, 'close']

    open = day_data.ix[day_index, 'open'] / close
    high = day_data.ix[day_index, 'high'] / close
    low = day_data.ix[day_index, 'low'] / close
    pct_chg = day_data.ix[day_index, 'pct_chg']
    vol = day_data.ix[day_index, 'vol']
    today_up = True if pct_chg > 0 else False

    yesterday_up = True if day_data.ix[day_index - 1, 'pct_chg'] > 0 else False
    yesterday_close = day_data.ix[day_index - 1, 'close']
    yesterday_vol = day_data.ix[day_index - 1, 'vol']
    yesterday_ma30 = day_data.ix[day_index - 1, 'ma30']
    yesterday_ma_up = True if yesterday_close > yesterday_ma30 else False
    vol_compare = vol / yesterday_vol

    ma5 = day_data.ix[day_index, 'ma5'] / close
    ma10 = day_data.ix[day_index, 'ma10'] / close
    ma20 = day_data.ix[day_index, 'ma20'] / close
    ma30 = day_data.ix[day_index, 'ma30'] / close
    ma60 = day_data.ix[day_index, 'ma60'] / close
    ma90 = day_data.ix[day_index, 'ma90'] / close
    ma120 = day_data.ix[day_index, 'ma120'] / close
    ma150 = day_data.ix[day_index, 'ma150'] / close
    ma_min = np.min([ma5, ma10, ma20, ma30, ma60, ma90, ma120, ma150])
    ma_mean = np.mean([ma5, ma10, ma20, ma30, ma60, ma90, ma120, ma150])
    ma_max = np.max([ma5, ma10, ma20, ma30, ma60, ma90, ma120, ma150])
    ma_std = np.std([ma5, ma10, ma20, ma30, ma60, ma90, ma120, ma150])

    ma_v_5 = day_data.ix[day_index, 'ma_v_5'] / vol
    ma_v_10 = day_data.ix[day_index, 'ma_v_10'] / vol
    ma_v_20 = day_data.ix[day_index, 'ma_v_20'] / vol
    ma_v_30 = day_data.ix[day_index, 'ma_v_30'] / vol
    ma_v_60 = day_data.ix[day_index, 'ma_v_60'] / vol
    ma_v_90 = day_data.ix[day_index, 'ma_v_90'] / vol
    ma_v_120 = day_data.ix[day_index, 'ma_v_120'] / vol
    ma_v_150 = day_data.ix[day_index, 'ma_v_150'] / vol
    ma_v_min = np.min([ma_v_5, ma_v_10, ma_v_20, ma_v_30, ma_v_60, ma_v_90, ma_v_120, ma_v_150])
    ma_v_mean = np.mean([ma_v_5, ma_v_10, ma_v_20, ma_v_30, ma_v_60, ma_v_90, ma_v_120, ma_v_150])
    ma_v_max = np.max([ma_v_5, ma_v_10, ma_v_20, ma_v_30, ma_v_60, ma_v_90, ma_v_120, ma_v_150])
    ma_v_std = np.std([ma_v_5, ma_v_10, ma_v_20, ma_v_30, ma_v_60, ma_v_90, ma_v_120, ma_v_150])

    week_ma = week_data[week_data['trade_date'] <= trade_date]
    week_ma5 = week_ma.tail(1)['ma5'].values[0] / close
    week_ma10 = week_ma.tail(1)['ma10'].values[0] / close
    week_ma20 = week_ma.tail(1)['ma20'].values[0] / close
    week_ma30 = week_ma.tail(1)['ma30'].values[0] / close
    week_min = np.min([week_ma5, week_ma10, week_ma20, week_ma30])
    week_mean = np.mean([week_ma5, week_ma10, week_ma20, week_ma30])
    week_max = np.max([week_ma5, week_ma10, week_ma20, week_ma30])
    week_std = np.std([week_ma5, week_ma10, week_ma20, week_ma30])

    week_v_5 = week_ma.tail(1)['ma_v_5'].values[0] / vol
    week_v_10 = week_ma.tail(1)['ma_v_10'].values[0] / vol
    week_v_20 = week_ma.tail(1)['ma_v_20'].values[0] / vol
    week_v_30 = week_ma.tail(1)['ma_v_30'].values[0] / vol
    week_v_min = np.min([week_v_5, week_v_10, week_v_20, week_v_30])
    week_v_mean = np.mean([week_v_5, week_v_10, week_v_20, week_v_30])
    week_v_max = np.max([week_v_5, week_v_10, week_v_20, week_v_30])
    week_v_std = np.std([week_v_5, week_v_10, week_v_20, week_v_30])

    hs300_index = hs300_data[hs300_data['trade_date'] == trade_date].index.values[0]
    hs300_close = hs300_data.ix[hs300_index, 'close']
    hs300_open = hs300_data.ix[hs300_index, 'open'] / hs300_close
    hs300_high = hs300_data.ix[hs300_index, 'high'] / hs300_close
    hs300_low = hs300_data.ix[hs300_index, 'low'] / hs300_close
    hs300_pct_chg = hs300_data.ix[hs300_index, 'pct_chg']
    hs300_vol = hs300_data.ix[hs300_index, 'vol']
    hs300_today_up = True if hs300_pct_chg > 0 else False

    hs300_yesterday_up = True if hs300_data.ix[hs300_index - 1, 'pct_chg'] > 0 else False
    hs300_yesterday_close = hs300_data.ix[hs300_index - 1, 'close']
    hs300_yesterday_vol = hs300_data.ix[hs300_index - 1, 'vol']
    hs300_yesterday_ma30 = hs300_data.ix[hs300_index - 1, 'ma30']
    hs300_yesterday_ma_up = True if hs300_yesterday_close > hs300_yesterday_ma30 else False
    hs300_vol_compare = hs300_vol / hs300_yesterday_vol

    hs300_ma5 = hs300_data.ix[hs300_index, 'ma5'] / hs300_close
    hs300_ma10 = hs300_data.ix[hs300_index, 'ma10'] / hs300_close
    hs300_ma20 = hs300_data.ix[hs300_index, 'ma20'] / hs300_close
    hs300_ma30 = hs300_data.ix[hs300_index, 'ma30'] / hs300_close
    hs300_ma60 = hs300_data.ix[hs300_index, 'ma60'] / hs300_close
    hs300_ma90 = hs300_data.ix[hs300_index, 'ma90'] / hs300_close
    hs300_ma120 = hs300_data.ix[hs300_index, 'ma120'] / hs300_close
    hs300_ma150 = hs300_data.ix[hs300_index, 'ma150'] / hs300_close
    hs300_ma_min = np.min(
        [hs300_ma5, hs300_ma10, hs300_ma20, hs300_ma30, hs300_ma60, hs300_ma90, hs300_ma120, hs300_ma150])
    hs300_ma_mean = np.mean(
        [hs300_ma5, hs300_ma10, hs300_ma20, hs300_ma30, hs300_ma60, hs300_ma90, hs300_ma120, hs300_ma150])
    hs300_ma_max = np.max(
        [hs300_ma5, hs300_ma10, hs300_ma20, hs300_ma30, hs300_ma60, hs300_ma90, hs300_ma120, hs300_ma150])
    hs300_ma_std = np.std(
        [hs300_ma5, hs300_ma10, hs300_ma20, hs300_ma30, hs300_ma60, hs300_ma90, hs300_ma120, hs300_ma150])

    hs300_ma_v_5 = hs300_data.ix[hs300_index, 'ma_v_5'] / hs300_vol
    hs300_ma_v_10 = hs300_data.ix[hs300_index, 'ma_v_10'] / hs300_vol
    hs300_ma_v_20 = hs300_data.ix[hs300_index, 'ma_v_20'] / hs300_vol
    hs300_ma_v_30 = hs300_data.ix[hs300_index, 'ma_v_30'] / hs300_vol
    hs300_ma_v_60 = hs300_data.ix[hs300_index, 'ma_v_60'] / hs300_vol
    hs300_ma_v_90 = hs300_data.ix[hs300_index, 'ma_v_90'] / hs300_vol
    hs300_ma_v_120 = hs300_data.ix[hs300_index, 'ma_v_120'] / hs300_vol
    hs300_ma_v_150 = hs300_data.ix[hs300_index, 'ma_v_150'] / hs300_vol
    hs300_ma_v_min = np.min(
        [hs300_ma_v_5, hs300_ma_v_10, hs300_ma_v_20, hs300_ma_v_30, hs300_ma_v_60, hs300_ma_v_90, hs300_ma_v_120,
         hs300_ma_v_150])
    hs300_ma_v_mean = np.mean(
        [hs300_ma_v_5, hs300_ma_v_10, hs300_ma_v_20, hs300_ma_v_30, hs300_ma_v_60, hs300_ma_v_90, hs300_ma_v_120,
         hs300_ma_v_150])
    hs300_ma_v_max = np.max(
        [hs300_ma_v_5, hs300_ma_v_10, hs300_ma_v_20, hs300_ma_v_30, hs300_ma_v_60, hs300_ma_v_90, hs300_ma_v_120,
         hs300_ma_v_150])
    hs300_ma_v_std = np.std(
        [hs300_ma_v_5, hs300_ma_v_10, hs300_ma_v_20, hs300_ma_v_30, hs300_ma_v_60, hs300_ma_v_90, hs300_ma_v_120,
         hs300_ma_v_150])

    day_ma5_up = trend().ma_up(day_data, trade_date=trade_date, period=3, ma='ma5')
    day_ma5_down = trend().ma_down(day_data, trade_date=trade_date, period=3, ma='ma5')
    day_ma10_up = trend().ma_up(day_data, trade_date=trade_date, period=3, ma='ma10')
    day_ma10_down = trend().ma_down(day_data, trade_date=trade_date, period=3, ma='ma10')
    day_ma20_up = trend().ma_up(day_data, trade_date=trade_date, period=3, ma='ma20')
    day_ma20_down = trend().ma_down(day_data, trade_date=trade_date, period=3, ma='ma20')
    day_ma30_up = trend().ma_up(day_data, trade_date=trade_date, period=3, ma='ma30')
    day_ma30_down = trend().ma_down(day_data, trade_date=trade_date, period=3, ma='ma30')

    week_ma10_up = trend().ma_up(week_data, trade_date=trade_date, period=3, ma='ma10')
    week_ma10_down = trend().ma_down(week_data, trade_date=trade_date, period=3, ma='ma10')
    week_ma20_up = trend().ma_up(week_data, trade_date=trade_date, period=3, ma='ma20')
    week_ma20_down = trend().ma_down(week_data, trade_date=trade_date, period=3, ma='ma20')
    week_ma30_up = trend().ma_up(week_data, trade_date=trade_date, period=3, ma='ma30')
    week_ma30_down = trend().ma_down(week_data, trade_date=trade_date, period=3, ma='ma30')

    hs300_ma5_up = trend().ma_up(hs300_data, trade_date=trade_date, period=3, ma='ma5')
    hs300_ma5_down = trend().ma_down(hs300_data, trade_date=trade_date, period=3, ma='ma5')
    hs300_ma10_up = trend().ma_up(hs300_data, trade_date=trade_date, period=3, ma='ma10')
    hs300_ma10_down = trend().ma_down(hs300_data, trade_date=trade_date, period=3, ma='ma10')
    hs300_ma20_up = trend().ma_up(hs300_data, trade_date=trade_date, period=3, ma='ma20')
    hs300_ma20_down = trend().ma_down(hs300_data, trade_date=trade_date, period=3, ma='ma20')
    hs300_ma30_up = trend().ma_up(hs300_data, trade_date=trade_date, period=3, ma='ma30')
    hs300_ma30_down = trend().ma_down(hs300_data, trade_date=trade_date, period=3, ma='ma30')
    hs300_ma60_up = trend().ma_up(hs300_data, trade_date=trade_date, period=3, ma='ma60')
    hs300_ma60_down = trend().ma_down(hs300_data, trade_date=trade_date, period=3, ma='ma60')
    hs300_ma90_up = trend().ma_up(hs300_data, trade_date=trade_date, period=3, ma='ma90')
    hs300_ma90_down = trend().ma_down(hs300_data, trade_date=trade_date, period=3, ma='ma90')
    hs300_ma120_up = trend().ma_up(hs300_data, trade_date=trade_date, period=3, ma='ma120')
    hs300_ma120_down = trend().ma_down(hs300_data, trade_date=trade_date, period=3, ma='ma120')
    hs300_ma150_up = trend().ma_up(hs300_data, trade_date=trade_date, period=3, ma='ma150')
    hs300_ma150_down = trend().ma_down(hs300_data, trade_date=trade_date, period=3, ma='ma150')

    day_multi_up = trend().multi_ma_up(day_data.ix[day_index - 2:day_index, :], columns=['ma30', 'ma90', 'ma150'])
    day_multi_down = trend().multi_ma_down(day_data.ix[day_index - 2:day_index, :], columns=['ma30', 'ma90', 'ma150'])
    week_multi_up = trend().multi_ma_up(week_ma.tail(3), columns=['ma10', 'ma20', 'ma30'])
    week_multi_down = trend().multi_ma_down(week_ma.tail(3), columns=['ma10', 'ma20', 'ma30'])
    hs300_multi_up = trend().multi_ma_up(hs300_data.ix[day_index - 2:day_index, :], columns=['ma30', 'ma90', 'ma150'])
    hs300_multi_down = trend().multi_ma_down(hs300_data.ix[day_index - 2:day_index, :],
                                             columns=['ma30', 'ma90', 'ma150'])

    return [open, high, low, pct_chg, today_up, yesterday_up, yesterday_ma_up, vol_compare,
            ma5, ma10, ma20, ma30, ma60, ma90, ma120, ma150, ma_min, ma_mean, ma_max, ma_std,
            ma_v_5, ma_v_10, ma_v_20, ma_v_30, ma_v_60, ma_v_90, ma_v_120, ma_v_150,
            ma_v_min, ma_v_mean, ma_v_max, ma_v_std,
            week_ma5, week_ma10, week_ma20, week_ma30, week_min, week_mean, week_max, week_std,
            week_v_5, week_v_10, week_v_20, week_v_30, week_v_min, week_v_mean, week_v_max, week_v_std,
            hs300_open, hs300_high, hs300_low, hs300_pct_chg,
            hs300_today_up, hs300_yesterday_up, hs300_yesterday_ma_up, hs300_vol_compare,
            hs300_ma5, hs300_ma10, hs300_ma20, hs300_ma30, hs300_ma60, hs300_ma90, hs300_ma120, hs300_ma150,
            hs300_ma_min, hs300_ma_mean, hs300_ma_max, hs300_ma_std,
            hs300_ma_v_5, hs300_ma_v_10, hs300_ma_v_20, hs300_ma_v_30, hs300_ma_v_60, hs300_ma_v_90, hs300_ma_v_120,
            hs300_ma_v_150, hs300_ma_v_min, hs300_ma_v_mean, hs300_ma_v_max, hs300_ma_v_std,
            day_ma5_up, day_ma5_down, day_ma10_up, day_ma10_down,
            day_ma20_up, day_ma20_down, day_ma30_up, day_ma30_down,
            week_ma10_up, week_ma10_down, week_ma20_up, week_ma20_down, week_ma30_up, week_ma30_down,
            hs300_ma5_up, hs300_ma5_down, hs300_ma10_up, hs300_ma10_down, hs300_ma20_up, hs300_ma20_down,
            hs300_ma30_up, hs300_ma30_down, hs300_ma60_up, hs300_ma60_down, hs300_ma90_up, hs300_ma90_down,
            hs300_ma120_up, hs300_ma120_down, hs300_ma150_up, hs300_ma150_down,
            day_multi_up, day_multi_down, week_multi_up, week_multi_down, hs300_multi_up, hs300_multi_down]

def train_dt_classifier(train_X, train_y):
    clf = DecisionTreeClassifier()
    clf.fit(train_X, train_y)

    return clf

def train_gbdt_classifier(train_X, train_y):
    clf = GradientBoostingClassifier()
    clf.fit(train_X, train_y)

    return clf

def train_logistic_classifier(train_X, train_y):
    clf = LogisticRegression()
    clf.fit(train_X, train_y)

    return clf

def train_xgb_classifier(train_X, train_y):
    xgb_params = {'objective': 'binary:logistic', 'eta': 0.01, 'max_depth': 8, 'seed': 42, 'silent': 1,
                  'eval_metric': 'error'
                  ,'updater': 'grow_gpu'
                  }

    clf = XGBClassifier(**xgb_params)
    clf.fit(train_X, train_y)

    return clf

def predict_bool(classifier, test_X):
    return classifier.predict(test_X)


def predict_prob(classifier, test_X):
    return classifier.predict_proba(test_X)[:, 1]


def calc_precision(y_true, y_predict_bool):
    return precision_score(y_true=y_true, y_pred=y_predict_bool)


def calc_recall(y_true, y_predict_bool):
    return recall_score(y_true=y_true, y_pred=y_predict_bool)


def calc_auc(y_true, y_pred_prob):
    return roc_auc_score(y_true=y_true, y_score=y_pred_prob)
