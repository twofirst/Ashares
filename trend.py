import numpy as np


class trend(object):
    # def __init__(self):
    #     print()

    def ma_up(self, data, trade_date, period=3, ma='ma30'):
        price_ls = data[data['trade_date'] <= trade_date].tail(period)[ma].tolist()
        price = 0
        for i in np.arange(len(price_ls)):
            if price_ls[i] >= price:
                price = price_ls[i]
            else:
                return False
        else:
            return True

    def ma_up2(self, data, trade_date, period=10, ma='ma30'):
        price_ls = data[data['trade_date'] <= trade_date].tail(period+1)[ma].tolist()
        # if price_ls[0] >= price_ls[-1]:
        #     return False

        pos_cnt, neg_cnt, neu_cnt = 0, 0, 0
        for i in np.arange(1,len(price_ls)):
            if price_ls[i] >= price_ls[i-1]:
                pos_cnt+=1
            else:
                neg_cnt+=1

        return [pos_cnt,neg_cnt]

    def ma_down(self, data, trade_date, period=3, ma='ma30'):
        price_ls = data[data['trade_date'] <= trade_date].tail(period)[ma].tolist()
        price = 9999
        for i in np.arange(len(price_ls)):
            if price_ls[i] <= price:
                price = price_ls[i]
            else:
                return False
        else:
            return True

    def ma_score(self, data, trade_date, period=3, ma='ma30'):
        up = self.ma_up(data, trade_date, period, ma)
        down = self.ma_down(data, trade_date, period, ma)
        if up:
            return 1
        elif down:
            return 0
        else:
            return -1

    def multi_ma_up(self, samples, columns=['ma30', 'ma90', 'ma150']):
        for i in samples.index:
            price = 9999
            for col in columns:
                if samples.ix[i, col] < price:
                    price = samples.ix[i, col]
                else:
                    return False
        else:
            for col in columns:
                price = 0
                for i in samples.index:
                    if samples.ix[i, col] > price:
                        price = samples.ix[i, col]
                    else:
                        return False
            else:
                return True

    def multi_ma_down(self, samples, columns=['ma30', 'ma90', 'ma150']):
        for i in samples.index:
            price = 0
            for col in columns:
                if samples.ix[i, col] > price:
                    price = samples.ix[i, col]
                else:
                    return False
        else:
            for col in columns:
                price = 999
                for i in samples.index:
                    if samples.ix[i, col] < price:
                        price = samples.ix[i, col]
                    else:
                        return False
            else:
                return True
