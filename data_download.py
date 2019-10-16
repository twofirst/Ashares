import os
import time
import numpy as np
import pandas as pd
import tushare as ts


class data_download(object):
    def __init__(self):
        self.pro = ts.pro_api('d334f1680cb3c7416c20531cd836c7d8552df45a5a808e410d9e74c4')

    def code_transfer(self, code):
        if '.' not in code:
            if code[0] == '6':
                code = code + '.SH'
            else:
                code = code + '.SZ'

        return code

    def get_sz50(self):
        return ts.get_sz50s()

    def get_hs300(self):
        return ts.get_hs300s()

    def get_zz500(self):
        return ts.get_zz500s()

    def get_Astocks(self):
        data = None
        while data is None:
            try:
                data = self.pro.stock_basic(exchange='', list_status='L',
                                            fields='ts_code,symbol,name,area,industry,list_date')
                data.columns = ['ts_code', 'code', 'name', 'area', 'industry', 'list_date']
            except:
                time.sleep(1)
                continue

        return data

    def get_sh_index(self):
        return ts.pro_bar(api=self.pro, ts_code='000001.SH', asset='I', start_date='20000101',
                          end_date='20201231', ma=[5, 10, 20, 30, 60, 90, 120, 150])

    def get_sz_index(self):
        return ts.pro_bar(api=self.pro, ts_code='399300.SZ', asset='I', start_date='20000101',
                          end_date='20201231', ma=[5, 10, 20, 30, 60, 90, 120, 150])

    def get_sz50_index(self, start_date, end_date, ma=[5, 10, 20, 30, 60, 90, 120, 150]):
        try:
            data = ts.pro_bar(api=self.pro, ts_code='000016.SH', asset='I', start_date='20000101',
                              end_date='20201231', ma=ma)
            target = data[(data['trade_date'] >= start_date) & (data['trade_date'] <= end_date)]
            target = target.dropna()
            target = target.sort_values(by='trade_date', ascending=True)
            target.reset_index(drop=True, inplace=True)
        except:
            print('download sz50 index data error!')
        else:
            return target

    def get_hs300_index(self, start_date, end_date, ma=[5, 10, 20, 30, 60, 90, 120, 150]):
        target = None
        while target is None:
            try:
                data = ts.pro_bar(ts_code='000300.SH',api=self.pro,  asset='I', start_date='20000101',
                                  end_date='20201231', ma=ma)
                target = data[(data['trade_date'] >= start_date) & (data['trade_date'] <= end_date)]
                target = target.dropna()
                target = target.sort_values(by='trade_date', ascending=True)
                target.reset_index(drop=True, inplace=True)
            except:
                time.sleep(1)
                continue
                # print('download hs300 index data error!')

        return target

    def get_index_data(self, code, start_date, end_date):
        return self.pro.index_daily(ts_code=self.code_transfer(code), start_date=start_date, end_date=end_date)

    def get_core_stocks(self, index_code='000300.SZ'):
        try:
            data = self.pro.index_weight(index_code=index_code, start_date='20000101', end_date='20201231')
        except:
            print('download core stocks data error!')
        else:
            return data

    def calc_ma(self, data, ma_list=[5, 30]):
        for ma in ma_list:
            for i in np.arange(ma - 1, len(data)):
                slice = data.ix[data.index.intersection(np.arange(i - ma + 1, i + 1)), :]
                price_mean = round(slice['close'].mean(), 2)
                vol_mean = round(slice['vol'].mean(), 2)
                data.ix[i, 'ma' + str(ma)] = price_mean
                data.ix[i, 'ma_v_' + str(ma)] = vol_mean

        return data

    def get_stock_real_data(self, code):
        while True:
            try:
                df = ts.get_realtime_quotes(code)
                return df
            except:
                time.sleep(1)
                continue

    def get_stock_day_data(self, code, ma_list, start_date, end_date):
        code = self.code_transfer(code)
        target = None
        while target is None:
            try:
                data = ts.pro_bar(api=self.pro, ts_code=code, adj='qfq', ma=ma_list,
                                  start_date='20000101', end_date='20201231')
                data.dropna(inplace=True)
                target = data[(data['trade_date'] >= start_date) & (data['trade_date'] <= end_date)]
                target = target.sort_values(by='trade_date',ascending=True)
                target.reset_index(drop=True, inplace=True)
            except:
                # print(code, 'download day data error!')
                time.sleep(1)
                continue

        return target

    def get_stock_week_data(self, code, ma_list=[5, 10, 20, 30]):
        code = self.code_transfer(code)
        try:
            data = self.pro.weekly(ts_code=code, start_date='20000101', end_date='20201231',
                                   fields='trade_date,open,high,low,close,vol,amount')
            data = data.sort_values(by='trade_date', ascending=True)
            data.reset_index(drop=True, inplace=True)
            data = data_download().calc_ma(data, ma_list=ma_list)
            data.dropna(inplace=True)
            data.reset_index(drop=True, inplace=True)
        except:
            print(code, 'download week data error!')
            return pd.DataFrame()

        return data

    def get_margin(self, trade_date):
        return self.pro.margin(trade_date=trade_date)

    def load_stock_day_data(self, code, start_date, end_date):
        file_path = 'Data/' + code + '.csv'
        isExists = os.path.exists(file_path)
        if isExists:
            data = pd.read_csv(file_path)
            data['trade_date'] = data['trade_date']
            data = data[(data['trade_date'] >= int(start_date)) & (data['trade_date'] <= int(end_date))]
            data['trade_date'] = data['trade_date'].apply(lambda x: str(x))
            data.reset_index(drop=True, inplace=True)

            return data
        else:
            return self.get_stock_day_data(code, [5, 10, 20, 30, 120], start_date, end_date)