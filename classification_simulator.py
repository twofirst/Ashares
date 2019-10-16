import math
import numpy as np
import pandas as pd
from data_download import data_download
from trade import trade
from stragy import buy_stragy, sell_stragy
from models import *
from data_generation import whether_buy_condition, whether_sell_condition, get_ma_sort, get_feature_trend, \
    generate_features


def build_dummies(df):
    str_columns = []
    for c in df.columns[:]:
        if isinstance(df.loc[df.index[0], c], str):
            str_columns.append(c)
    dummies = pd.get_dummies(df[str_columns])
    df_2 = df.drop(columns=str_columns)

    return pd.concat([df_2, dummies], axis=1)


train = pd.read_csv('./Files/data_generation_20090101-20181231_2.csv', header=0)
train=train[train[train.columns[-10]]<20170101]
train = train[(train[train.columns[-14]] == 'ma20') & (train[train.columns[-13]] == 'ma20')]
train_X = train[train.columns[:-14]]
train_y = train[train.columns[[-12]]]

train_X = build_dummies(train_X)
train = pd.concat([train_X, train_y], axis=1)
train_pos = train[train[train.columns[-1]] == True]
train_neg = train[train[train.columns[-1]] == False]


pd.set_option('display.max_columns', 99)
pd.set_option('display.max_rows', 999)
start_date = '20170101'
end_date = '20191231'

astocks = data_download().get_Astocks()
# stocks = data_download().get_sz50()
stocks = data_download().get_hs300()
# stocks = data_download().get_zz500()
# stocks=astocks
stocks = stocks.merge(astocks, on=['code', 'name'])

# hs300_data = data_download().get_sz50_index(start_date, end_date, ma=[10, 20, 30, 120])
hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[5, 10, 20, 30, 120])

data = {}
for i in stocks.index[:]:
    code = stocks.ix[i, 'code']
    # industry = stocks.ix[i, 'industry']
    # if industry in filter:
    #     continue

    # if industry not in industries:
    #     continue

    # if code == '600372' or code == '002044':
    #     continue

    stock_data = data_download().load_stock_day_data(code, start_date=start_date, end_date=end_date)
    if stock_data is not None:
        data[code] = stock_data

while True:
    core_buy_ma = 'ma20'
    core_sell_ma = 'ma20'
    stock_code = ''
    money = 1000000
    max_stock = 3
    in_stock_dict = {}  # {code:{share_cnt:0,invest:0,buy_date:0}}
    records = []

    train_neg = train_neg.sample(len(train_pos), random_state=np.random.randint(100))
    train = train_pos.append(train_neg)
    train_X = train[train.columns[:-1]]
    train_y = train[train.columns[-1]]

    clf = train_xgb_classifier(train_X, train_y)

    for i in hs300_data.index:
        trade_date = hs300_data.ix[i, 'trade_date']
        if len(in_stock_dict) > 0:
            ls = list(in_stock_dict.keys())
            for stock_code in ls:
                stock_data = data.get(stock_code)
                if trade_date not in stock_data['trade_date'].values:
                    continue
                stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
                stock_close = stock_data.ix[stock_index, 'close']

                if whether_sell_condition(stock_data, stock_index, core_sell_ma):
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

        if len(in_stock_dict) < max_stock:
            candidates = []
            key_ls = []
            for key in data.keys():
                stock_data = data.get(key)
                if trade_date not in stock_data['trade_date'].values:
                    continue
                stock_idx = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
                if stock_idx >= 4 and whether_buy_condition(stock_data, stock_idx, core_buy_ma) and stock_data.ix[
                    stock_idx, 'close'] > stock_data.ix[stock_idx, core_sell_ma]:
                    key_ls.append(key)
                    candidates.append(generate_features(hs300_data, stock_data, trade_date))

            if len(candidates) > 0:
                candidates = pd.DataFrame(candidates)
                candidates.columns = [str(i) for i in np.arange(candidates.shape[1])]
                candidates = build_dummies(candidates)
                candidates = train_X.align(candidates, join='outer', axis=1, fill_value=0)[1]
                candidates = candidates[train_X.columns]
                prob_ls = list(predict_prob(clf, candidates))

                while len(prob_ls)>=1 and len(in_stock_dict) < max_stock:
                    prob_max = max(prob_ls)
                    if prob_max > 0.5:
                        stock_code = key_ls[prob_ls.index(prob_max)]
                        key_ls.remove(stock_code)
                        prob_ls.remove(prob_max)
                        stock_data = data.get(stock_code)
                        stock_index = stock_data[stock_data['trade_date'] == trade_date].index.values[0]
                        close = stock_data.ix[stock_index, 'close']
                        valid_money = money / (max_stock - len(in_stock_dict))
                        share_cnt = math.modf(valid_money / (close * 100))[1]

                        if share_cnt > 0:
                            invest = close * 100 * share_cnt
                            money -= invest
                            in_stock_flag = True
                            buy_date = trade_date
                            # {code:{share_cnt:0,invest:0,buy_date:0}}
                            in_stock_dict[stock_code] = {'share_cnt': share_cnt, 'invest': invest, 'buy_date': buy_date,
                                                         'buy_price': close}
                    else:
                        break
    else:
        if len(in_stock_dict) > 0:
            # print('money=',money,'in_stock_len=',len(in_stock_dict))
            ls = list(in_stock_dict.keys())
            for stock_code in ls:
                stock_data = data.get(stock_code)
                if trade_date not in stock_data['trade_date'].values:
                    invest = in_stock_dict.get(stock_code).get('invest')
                    money += invest
                    # print('without trade_date,stock_code=',stock_code,'money=',money)
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
                # print(record)
                in_stock_dict.pop(stock_code)

    if len(records) > 0:
        records = pd.DataFrame(records,
                               columns=['code', 'buy_date', 'sell_date', 'days', 'buy_price', 'sell_price', 'rate',
                                        'money'])
        success_rate = len(records[records['rate'] > 0]) / len(records)
        print('hs300',
              # 'hs300_close > hs300_ma20 and hs300_v_30 > hs300_v 120 and close>ma20 and close / pre_close <= 1.05',',
              # 'hs300_close > max(hs300_ma10_and_hs300_ma20_and_hs300_ma30) and close>ma20_and_close>ma30 and vol>ma_v_120 and close / pre_close <= 1.05',
              'hs300_close > hs300_ma20 and pre_close<pre_ma20 and close>min(ma20,ma30) and vol > max(pre_vol,ma_v_120) and close / pre_close <= 1.05',
              # 'hs300_close > hs300_ma20 and pre_close<pre_ma20 and close>max(ma20,ma30) and vol>ma_v_30 and ma_v_30>ma_v_120 and close / pre_close <= 1.05',
              'sell close<= max(stock_ma20,stock_ma30)', 'and max_stock=',
              max_stock, start_date, end_date, len(records), records['rate'].min(), records['rate'].mean(),
              records['rate'].max(), success_rate, money / 1000000, True if money > 1000000 else False)

        # if money / 1000000 > 15:
        #     print(records[['code', 'buy_date', 'sell_date', 'days', 'buy_price', 'sell_price', 'rate']])
