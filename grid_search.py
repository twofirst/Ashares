import numpy as np
import pandas as pd
from data_download import data_download

pd.set_option('display.max_columns', 99)
pd.set_option('display.max_rows', 99)
np.set_printoptions(suppress=True)


def compare_value(df):
    df['close_None'] = True
    df['close>ma10'] = df['close'] > df['ma10']
    df['close>ma20'] = df['close'] > df['ma20']
    df['close>ma30'] = df['close'] > df['ma30']
    df['close>ma10_or_ma20'] = df['close>ma10'] | df['close>ma20']
    df['close>ma10_and_ma20'] = df['close>ma10'] & df['close>ma20']
    df['close>ma20_or_ma30'] = df['close>ma20'] | df['close>ma30']
    df['close>ma20_and_ma30'] = df['close>ma20'] & df['close>ma30']

    df['increase_rate'] = df['close'] / df['pre_close']

    df['vol_None'] = True
    df['vol>vol30'] = df['vol'] > df['ma_v_30']
    df['vol>vol120'] = df['vol'] > df['ma_v_120']
    df['vol30>vol120'] = df['ma_v_30'] > df['ma_v_120']
    df['vol>vol30_or_vol120'] = df['vol>vol30'] | df['vol>vol120']
    df['vol>vol30_and_vol120'] = df['vol>vol30'] & df['vol>vol120']
    df['vol>vol30_vol30>vol120'] = df['vol>vol30'] & df['vol30>vol120']

    return df


def trade_stock(code, index_condition, buy_vol_condition, buy_close_condition, sell_condition, close_increase_rate):
    stock_data = data.get(code).copy()
    stock_condition = stock_data.merge(index_condition, on='trade_date')
    stock_condition.ix[stock_condition.index[-1], sell_condition] = False
    stock_data['close_rate_boolean'] = stock_data['increase_rate'] <= close_increase_rate
    stock_condition['stock_mean'] = stock_data[[buy_vol_condition, buy_close_condition, 'close_rate_boolean']].mean(
        axis=1)
    stock_condition['condition_mean'] = stock_condition[['index_mean', 'stock_mean']].mean(
        axis=1)
    stock_condition['trade'] = stock_condition['condition_mean'] * stock_condition[
        sell_condition]
    pre_trade = [0]
    pre_trade.extend(stock_condition[:-1]['trade'].tolist())
    stock_condition['pre_trade'] = pd.Series(pre_trade)
    stock_condition['diff'] = stock_condition['trade'] - stock_condition['pre_trade']
    stock_condition['buy'] = stock_condition['diff'] == 1
    stock_condition['sell'] = (stock_condition['diff'] < 0) & (stock_condition['trade'] == 0)
    candidates = stock_condition[
        (stock_condition['buy']) | (stock_condition['sell'])].reset_index(
        drop=True)
    instock = [0]
    instock.extend(candidates[:-1]['buy'].tolist())
    candidates['sell'] = candidates['sell'] * pd.Series(instock)
    buy = candidates[candidates['buy'] == True].reset_index(drop=True)
    sell = candidates[candidates['sell'] == 1].reset_index(drop=True)

    if len(buy) != len(sell):
        print(code, 'buy_cnt:', len(buy), 'sell_cnt:', len(sell))
    else:
        return list(sell['close'] * (1 - 0.002) / buy['close'])


def get_trade_statistic(trade_record_ls):
    trade_record_df = pd.DataFrame(trade_record_ls, columns=['rate'])
    failed = trade_record_df[trade_record_df['rate'] < 1]
    succeeded = trade_record_df[trade_record_df['rate'] > 1]

    return np.round([len(trade_record_df), len(succeeded) / len(trade_record_df), trade_record_df['rate'].mean() - 1,
                     trade_record_df['rate'].std(), trade_record_df['rate'].prod() - 1,
                     failed['rate'].min() - 1, failed['rate'].mean() - 1, succeeded['rate'].mean() - 1,
                     succeeded['rate'].max() - 1], 3)


def get_class_code_list(hs300_class, stock_class):
    if stock_class == 'All':
        class_stock_ls = hs300_class['code'].values.tolist()
    elif stock_class == 'NoPeriod':
        class_stock_ls = hs300_class[hs300_class['class'] != 'Period'][
            'code'].values.tolist()
    elif stock_class == 'NoFinancial':
        class_stock_ls = hs300_class[hs300_class['class'] != 'Financial'][
            'code'].values.tolist()
    else:
        class_stock_ls = hs300_class[hs300_class['class'] == stock_class][
            'code'].values.tolist()

    return class_stock_ls


if __name__ == '__main__':
    base_path = '/home/twofirst/Documents/Astock/grid_simulator/'
    compare_file = base_path + 'grid_search_compare_results_6.csv'
    compare_records = []
    start_date = '20090101'
    end_date = '20181231'
    astocks = data_download().get_Astocks()
    stocks = data_download().get_hs300()
    stocks = stocks.merge(astocks, on=['code', 'name'])
    index_data = data_download().get_hs300_index(start_date, end_date, ma=[5, 10, 20, 30, 120])
    index_data = compare_value(index_data)
    hs300_class = pd.read_table('HS300_class.txt', header=0, dtype='str')

    data = {}
    for i in stocks.index[:]:
        code = stocks.ix[i, 'code']
        stock_data = data_download().load_stock_day_data(code, start_date=start_date, end_date=end_date)
        if stock_data is not None:
            data[code] = compare_value(stock_data)

    for index_close_condition in ['close>ma10_or_ma20','close>ma10_and_ma20', 'close>ma20_or_ma30', 'close>ma20_and_ma30']:
        # 'close_None', 'close>ma30', 'close>ma20', 'close>ma10'
        for index_vol_condition in ['vol>vol30', 'vol>vol120', 'vol30>vol120', 'vol>vol30_or_vol120',
                                    'vol>vol30_and_vol120', 'vol>vol30_vol30>vol120', 'vol_None']:
            index_condition = index_data[['trade_date']].copy()
            index_condition['index_mean'] = index_data[[index_close_condition, index_vol_condition]].mean(axis=1)

            for buy_vol_condition in ['vol>vol30', 'vol>vol120', 'vol30>vol120', 'vol>vol30_or_vol120',
                                      'vol>vol30_and_vol120', 'vol>vol30_vol30>vol120', 'vol_None']:
                for buy_close_condition in ['close>ma10', 'close>ma20', 'close>ma30', 'close>ma10_or_ma20',
                                            'close>ma10_and_ma20', 'close>ma20_or_ma30', 'close>ma20_and_ma30']:
                    for sell_condition in ['close>ma10', 'close>ma20', 'close>ma30', 'close>ma10_or_ma20',
                                           'close>ma10_and_ma20', 'close>ma20_or_ma30', 'close>ma20_and_ma30']:
                        for close_increase_rate in np.arange(1.01, 1.06, 0.01):
                            record_dict = {}
                            for code in data.keys():
                                record_dict[code] = trade_stock(code, index_condition, buy_vol_condition,
                                                                buy_close_condition, sell_condition,
                                                                close_increase_rate)
                            else:
                                for stock_class in ['Other', 'Period', 'Financial', 'NoPeriod', 'NoFinancial', 'All']:
                                    trade_record_ls = []
                                    class_stock_ls = get_class_code_list(hs300_class, stock_class)

                                    for code, ls in record_dict.items():
                                        if code in class_stock_ls:
                                            trade_record_ls.extend(ls)
                                    else:

                                        statistic_record = [index_close_condition, index_vol_condition,
                                                            buy_vol_condition, buy_close_condition, sell_condition,
                                                            close_increase_rate, stock_class]
                                        statistic_record.extend(get_trade_statistic(trade_record_ls))
                                        compare_records.append(statistic_record)
                                        print(len(compare_records), statistic_record)

                    else:
                        df = pd.DataFrame(compare_records)
                        df.columns = ['index_close_condition', 'index_vol_condition', 'buy_vol_condition',
                                      'buy_close_condition', 'sell_condition', 'close_increase_rate', 'stock_class',
                                      'trade_times', 'success_rate', 'rate_mean', 'rate_std', 'accumulated_rate',
                                      'failed_rate_min', 'failed_rate_mean', 'succeeded_rate_mean',
                                      'succeeded_rate_max']
                        df.to_csv(compare_file, index=False)
