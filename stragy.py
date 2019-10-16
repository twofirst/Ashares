import pandas as pd
from trend import trend


class buy_stragy(object):

    def ma_stragy(self, day_data, week_data, hs300_data, index, ma='ma30'):
        close = day_data.ix[index, 'close']
        vol = day_data.ix[index, 'vol']
        high = day_data.ix[index, 'high']
        change = day_data.ix[index, 'change']
        pct_chg = day_data.ix[index, 'pct_chg']
        pre_close = day_data.ix[index - 1, 'close']
        pre_vol = day_data.ix[index - 1, 'vol']
        # pre_ma = day_data.ix[index - 1, ma]
        trade_date = day_data.ix[index, 'trade_date']
        day_ma_price = day_data.ix[index, ma]
        # week_ma = week_data[week_data['trade_date'] <= trade_date]
        hs300_index = hs300_data[hs300_data['trade_date'] == trade_date].index.values[0]
        hs300_close = hs300_data.ix[hs300_index, 'close']
        hs300_ma = hs300_data.ix[hs300_index, ma]
        hs300_vol = hs300_data.ix[hs300_index, 'vol']
        hs300_ma_v_30 = hs300_data.ix[hs300_index, 'ma_v_30']
        hs300_ma_v_120 = hs300_data.ix[hs300_index, 'ma_v_120']

        flag = hs300_close > hs300_ma and hs300_vol > hs300_ma_v_120 and hs300_ma_v_30 > hs300_ma_v_120

        # ma_status = trend().ma_up2(data=hs300_data, trade_date=trade_date, period=10, ma='ma_v_120')
        if close > day_ma_price and vol > pre_vol and change > 0 and not (pct_chg >= 9.9 and high == close) and \
                flag:
            return True
        else:
            return False


class sell_stragy(object):

    def ma_stragy(self, day_data, week_data, index, ma='ma30'):
        close = day_data.ix[index, 'close']
        ma = day_data.ix[index, ma]
        if close < ma:
            return True
        else:
            return False
