import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 99)
pd.set_option('display.max_columns', 99)

data_1 = pd.read_csv('/home/twofirst/Documents/Astock/grid_simulator/grid_search2_compare_results_close_ma10_ma20.csv',
                   header=0, sep=',')
data = pd.read_csv('/home/twofirst/Documents/Astock/grid_simulator/grid_search2_compare_results_close_ma20_ma30.csv',
                   header=0, sep=',')
# data = pd.read_csv('/home/twofirst/Documents/Astock/grid_simulator/test_grid_search_close_ma10_ma20_and_close_ma20_ma30_weight.csv',
#                    header=0, sep=',')
# data=data_1.append(data_2)
# print(len(data_1),len(data_2),len(data))
# data['weight'] = pow(data['accumulated_rate'], 1 / data['trade_times'])
# data['ex'] = data['rate_mean']*data['trade_times']
#
# print(len(data))
# data = data.dropna()
# print(len(data))
# data = data[data['accumulated_rate'] > 1]
data = data[data['rate_mean'] > 0]
# print(len(data))
data = data[data['stock_class'] == 'All']
# data = data[(data['stock_class'] == 'Financial') | (data['stock_class'] == 'Other')]
# print(len(data))
# data=data.sort_values(by='weight',ascending=False)
# data=data.reset_index(drop=True)

print(data.columns)
# print(data)
# data.to_csv('/home/twofirst/Documents/Astock/grid_simulator/grid_search2_compare_results_close_ma10_ma20_and_close_ma20_ma30_weight.csv',index=False)

# condition = ['stock_class']
# condition = ['index_close_condition','index_vol_condition','buy_close_condition', 'buy_vol_condition','stock_class']
# grp = data.groupby(condition)
# print(grp.mean().sort_values(by='weight', ascending=False)[
#           ['earn_base', 'trade_times', 'success_rate', 'rate_mean']])
# print(grp.mean().sort_values(by='success_rate', ascending=True)[['trade_times','success_rate','ex','rate_mean']])
# print(grp.mean().sort_values(by='rate', ascending=False)[['rate']])
# print('------------------------------------------------------------')

index_close_condition = "('ma30', 'ma20', 'close')"
index_vol_condition = "('ma_v_30', 'ma_v_120', 'vol')"
# buy_vol_condition = "('ma_v_30', 'ma_v_120', 'vol')"
# buy_close_condition = "('ma30', 'ma20', 'close')"
close_increase_rate = 1.05
# stock_class = "Other"
sell_condition = "close<ma20"
target = data[
    (data['index_close_condition'] == index_close_condition)
    & (data['index_vol_condition'] == index_vol_condition)
#     & (data['buy_vol_condition'] == buy_vol_condition)
#     & (data['buy_close_condition'] == buy_close_condition)
    & (data['close_increase_rate'] == close_increase_rate)
#     & (data['stock_class'] == stock_class)
    & (data['sell_condition'] == sell_condition)
    ]

target=target.sort_values(by='success_rate')
print(target[['buy_close_condition','buy_vol_condition','stock_class','trade_times','success_rate','rate_mean']])