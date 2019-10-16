import math
import time
import datetime
import pandas as pd
from models import *
from position_management import position_manager


class trade(object):

    def __init__(self, hs300_data, buy_stragy, sell_stragy):
        self.initial_money = 1000000
        self.hs300_data = hs300_data
        self.buy_stragy = buy_stragy
        self.sell_stragy = sell_stragy
        self.records_info = []

    def get_records_info(self):
        records = pd.DataFrame(self.records_info, columns=[
            'open', 'high', 'low', 'pct_chg', 'today_up', 'yesterday_up', 'yesterday_ma_up', 'vol_compare',
            'ma5', 'ma10', 'ma20', 'ma30', 'ma60', 'ma90', 'ma120', 'ma150', 'ma_min', 'ma_mean', 'ma_max', 'ma_std',
            'ma_v_5', 'ma_v_10', 'ma_v_20', 'ma_v_30', 'ma_v_60', 'ma_v_90', 'ma_v_120', 'ma_v_150',
            'ma_v_min', 'ma_v_mean', 'ma_v_max', 'ma_v_std',
            'week_ma5', 'week_ma10', 'week_ma20', 'week_ma30', 'week_min', 'week_mean', 'week_max', 'week_std',
            'week_v_5', 'week_v_10', 'week_v_20', 'week_v_30', 'week_v_min', 'week_v_mean', 'week_v_max', 'week_v_std',
            'hs300_open', 'hs300_high', 'hs300_low', 'hs300_pct_chg', 'hs300_today_up', 'hs300_yesterday_up',
            'hs300_yesterday_ma_up', 'hs300_vol_compare',
            'hs300_ma5', 'hs300_ma10', 'hs300_ma20', 'hs300_ma30', 'hs300_ma60', 'hs300_ma90',
            'hs300_ma120', 'hs300_ma150', 'hs300_ma_min', 'hs300_ma_mean', 'hs300_ma_max', 'hs300_ma_std',
            'hs300_ma_v_5', 'hs300_ma_v_10', 'hs300_ma_v_20', 'hs300_ma_v_30', 'hs300_ma_v_60', 'hs300_ma_v_90',
            'hs300_ma_v_120', 'hs300_ma_v_150', 'hs300_ma_v_min', 'hs300_ma_v_mean', 'hs300_ma_v_max', 'hs300_ma_v_std',
            'day_ma5_up', 'day_ma5_down', 'day_ma10_up', 'day_ma10_down',
            'day_ma20_up', 'day_ma20_down', 'day_ma30_up', 'day_ma30_down',
            'week_ma10_up', 'week_ma10_down', 'week_ma20_up', 'week_ma20_down', 'week_ma30_up', 'week_ma30_down',
            'hs300_ma5_up', 'hs300_ma5_down', 'hs300_ma10_up', 'hs300_ma10_down', 'hs300_ma20_up', 'hs300_ma20_down',
            'hs300_ma30_up', 'hs300_ma30_down', 'hs300_ma60_up', 'hs300_ma60_down', 'hs300_ma90_up', 'hs300_ma90_down',
            'hs300_ma120_up', 'hs300_ma120_down', 'hs300_ma150_up', 'hs300_ma150_down', 'day_multi_up',
            'day_multi_down', 'week_multi_up', 'week_multi_down', 'hs300_multi_up', 'hs300_multi_down',
            'rate', 'success'
        ])

        return records

    def calc_trade_days(self, buy_date, sell_date):
        date1 = time.strptime(str(buy_date), "%Y%m%d")
        date2 = time.strptime(str(sell_date), "%Y%m%d")
        d1 = datetime.date(date1[0], date1[1], date1[2])
        d2 = datetime.date(date2[0], date2[1], date2[2])
        days = (d2 - d1).days

        return days

    def buy_sell(self, day_data, week_data):
        records = []
        share_cnt = 0
        fail_times = 0

        money = self.initial_money
        in_stock_flag = False
        position = position_manager()

        for i in day_data.index[2:]:
            row = day_data.ix[i, :]
            trade_date = row['trade_date']
            week_ma = week_data[week_data['trade_date'] <= trade_date]
            # if len(week_ma) == 0:
            #     continue

            if not in_stock_flag and self.buy_stragy(day_data, week_data, self.hs300_data, index=i):
                # info = record_info(day_data, week_data, self.hs300_data, day_index=i)

                # position_rate = 1
                position_rate = position.attempt_trade(fail_times)
                share_cnt = math.modf(int(money * position_rate) / (row['close'] * 100))[1]
                if share_cnt > 0:
                    invest = row['close'] * 100 * share_cnt
                    money -= invest
                    in_stock_flag = True
                    buy_date = row['trade_date']
            elif in_stock_flag and self.sell_stragy(day_data, week_data, index=i):
                stock_value= row['close'] * 100 * share_cnt * (1 - 0.002)
                rate = round((stock_value - invest) / (money+invest), 2)
                success = True if rate > 0 else False
                money+=stock_value
                share_cnt = 0
                in_stock_flag = False
                sell_date = row['trade_date']
                days = self.calc_trade_days(buy_date, sell_date)

                records.append(
                    [buy_date, sell_date, days, rate, success, money])

                if success:
                    fail_times = 0
                else:
                    fail_times += 1

                # print(buy_date, sell_date, days,row['close'], rate)

                # pred_2 = predict_bool(self.clf_2, np.matrix(info))[0]
                # prob_2=predict_prob(self.clf_2, np.matrix(info))[0]
                # if rate<=0 and not pred_2:
                #     print(buy_date, sell_date, days, rate, pred_2,prob_2)

                # info.append(rate)
                # info.append(success)
                # self.records_info.append(info)
        else:
            if share_cnt > 0:
                stock_value= row['close'] * 100 * share_cnt * (1 - 0.002)
                rate = round((stock_value - invest) / (money+invest), 2)
                success = True if rate > 0 else False
                money+=stock_value
                sell_date = row['trade_date']
                days = self.calc_trade_days(buy_date, sell_date)
                records.append(
                    [buy_date, sell_date, days, rate, success, money])
                # info.append(rate)
                # info.append(success)
                # self.records_info.append(info)

        return pd.DataFrame(records,
                            columns=['buy_date', 'sell_date', 'contain_days', 'earn_rate', 'success', 'money'])
