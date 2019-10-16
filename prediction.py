import numpy as np
import pandas as pd
from models import *

origin_train = pd.read_csv('./Files/data_generation_core_buy20_sell20_vol_30_120_index_bull_20090101-20151231.csv', header=0)
origin_test = pd.read_csv('./Files/data_generation_core_buy20_sell20_vol_30_120_index_bull_20160101-20181231.csv', header=0)

for core_buy_ma in ['ma20']:
    for core_sell_ma in ['ma20']:
        # print(core_buy_ma,core_sell_ma)
        data_train = origin_train[(origin_train[origin_train.columns[-14]] == core_buy_ma) & (
                    origin_train[origin_train.columns[-13]] == core_sell_ma)]
        data_test = origin_test[(origin_test[origin_test.columns[-14]] == core_buy_ma) & (
                    origin_test[origin_test.columns[-13]] == core_sell_ma)]
        # data_train=origin_train.copy()
        # data_test=origin_test.copy()

        data = data_train.append(data_test)
        data.reset_index(drop=True, inplace=True)
        # print(data_train.shape,data_test.shape,data.shape)

        data_X = data[data.columns[47:-12]]
        data_y = data[data.columns[[-12]]]

        str_columns = []
        for c in data_X.columns[:]:
            if isinstance(data_X.loc[0, c], str):
                str_columns.append(c)
        dummies = pd.get_dummies(data_X[str_columns])
        data_X = data_X.drop(columns=str_columns)
        # data = pd.concat([data_X, dummies, data_y], axis=1)
        data = pd.concat([dummies, data_y], axis=1)
        # print(list(data.columns))

        data_train = data.head(len(data_train))
        train_pos = data_train[data_train[data_train.columns[-1]] == True]
        train_neg = data_train[data_train[data_train.columns[-1]] == False]
        data_test = data.tail(len(data_test))
        test_pos = data_test[data_test[data_test.columns[-1]] == True]
        test_neg = data_test[data_test[data_test.columns[-1]] == False]
        # print(len(data_train), len(train_pos), len(train_neg),len(data_test), len(test_pos), len(test_neg))

        for i in np.arange(200):
            train_neg_sample = train_neg.sample(len(train_pos), random_state=i)
            test_neg_sample = test_neg.sample(len(test_pos), random_state=i)
            test_neg_sample=test_neg
            train = train_pos.append(train_neg_sample)
            test = test_pos.append(test_neg_sample)
            # test = data_test.sample(int(len(data_test) * 0.5), random_state=i)

            train_X = train[train.columns[:-1]]
            test_X = test[test.columns[:-1]]
            train_y = train[train.columns[-1]]
            test_y = test[test.columns[-1]]

            # clf=train_dt_classifier(train_X,train_y)
            clf = train_xgb_classifier(train_X, train_y)
            # clf=train_gbdt_classifier(train_X,train_y)
            pred_bool = predict_bool(clf, test_X)
            pred_prob = predict_prob(clf, test_X)
            # print(core_buy_ma,core_sell_ma,calc_precision(test_y, pred_bool), calc_recall(test_y, pred_bool), calc_auc(test_y, pred_bool),
            #       calc_auc(test_y, pred_prob), len(test_pos), sum(pred_bool), len(test_neg_sample), len(pred_bool) - sum(pred_bool))
            print(core_buy_ma, core_sell_ma, calc_precision(test_y, pred_bool), calc_recall(test_y, pred_bool),
                  calc_auc(test_y, pred_bool), calc_auc(test_y, pred_prob))

            del clf
            # from feature_rank import *
            # rank_features_xgb(train_X,train_y)
            # rank_features_gbdt(train_X,train_y)

            # break
            df = origin_test[(origin_test[origin_test.columns[-14]] == core_buy_ma) & (
                    origin_test[origin_test.columns[-13]] == core_sell_ma)]
            df.reset_index(drop=True, inplace=True)
            result = pd.concat([df[df.columns[-12:]], pd.Series(pred_bool, name='pred')], axis=1)
            # print(result['109'].prod(), result[result['98'] == True]['109'].prod(),
            #       result[result['pred'] == True]['109'].prod())
            # print('----------------------')
