import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import GradientBoostingClassifier


def statistics(row):
    describe = row.describe()
    return describe


def rank_features_xgb(train_X, train_y):
    import operator
    from matplotlib import pylab as plt
    from xgboost import XGBClassifier
    from matplotlib import pyplot
    from xgboost import plot_importance

    def ceate_feature_map(features):
        outfile = open('xgb.fmap', 'w')
        i = 0
        for feat in features:
            outfile.write('{0}\t{1}\tq\n'.format(i, feat))
            i = i + 1

        outfile.close()

    # features=train_X.columns
    # ceate_feature_map(features)
    #
    xgb_params = {'objective': 'binary:logistic', 'eta': 0.01, 'max_depth': 8, 'seed': 42, 'silent': 1,
                  'eval_metric': 'error'
                  ,'updater': 'grow_gpu'
                  }
    # num_rounds = 1000
    #
    # dtrain = xgb.DMatrix(train_X, label=train_y)
    # gbdt = xgb.train(xgb_params, dtrain, num_rounds)
    #
    # importance = gbdt.get_fscore(fmap='xgb.fmap')
    # importance = sorted(importance.items(), key=operator.itemgetter(1))
    #
    # df = pd.DataFrame(importance, columns=['feature', 'fscore'])
    # df['fscore'] = df['fscore'] / df['fscore'].sum()
    # print(df)
    # df=df.tail(50)
    #
    # plt.figure()
    # df.plot()
    # df.plot(kind='barh', x='feature', y='fscore', legend=False, figsize=(6, 10))
    # plt.title('XGBoost Feature Importance')
    # plt.xlabel('relative importance')
    # plt.gcf().savefig('feature_importance_xgb.png')

    model = XGBClassifier(**xgb_params)
    model.fit(train_X, train_y)
    df = pd.concat([pd.Series(train_X.columns, name=0), pd.Series(model.feature_importances_, name=1)], axis=1)
    df.sort_values(by=1, ascending=True, inplace=True)

    print(df.tail(20))
    print(df[df[0] == 'tag'])
    print(sum(df[1]))
    print(sum(df.tail(100)[1]))
    # plot feature importance
    # plot_importance(model)
    # pyplot.show()


def rank_features_gbdt(train_X, train_y):
    # Build a forest and compute the feature importances
    from sklearn.ensemble import ExtraTreesClassifier
    forest = ExtraTreesClassifier(n_estimators=250, random_state=0)


    forest.fit(train_X, train_y)
    importances = forest.feature_importances_
    std = np.std([tree.feature_importances_ for tree in forest.estimators_], axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print("Feature ranking:")

    for f in range(train_X.shape[1]):
        print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]),train_X.columns[indices[f]])

    # Plot the feature importances of the forest
    # plt.figure()
    # plt.title("Feature importances")
    # plt.bar(range(train_X.shape[1]), importances[indices],
    #         color="r", yerr=std[indices], align="center")
    # plt.xticks(range(train_X.shape[1]), indices)
    # plt.xlim([-1, train_X.shape[1]])
    # plt.show()
