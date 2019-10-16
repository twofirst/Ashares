import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from data_download import data_download

code='000001.SZ'
start_date = '20120101'
end_date = '20121231'
ma = [5, 10, 20, 30, 60, 90, 120]
data = data_download().get_hs300_index(start_date, end_date, ma=[30, 60, 90,120])
# data = data_download().get_stock_day_data(code,[10, 20, 30,60,90,120],start_date, end_date)
print(data.columns)

# data['close']=(data['close'].max()-data['close'])/(data['close'].max()-data['close'].min())
# data['ma_v_5']=(data['ma_v_5'].max()-data['ma_v_5'])/(data['ma_v_5'].max()-data['ma_v_5'].min())
# data['ma_v_10']=(data['ma_v_10'].max()-data['ma_v_10'])/(data['ma_v_10'].max()-data['ma_v_10'].min())
# data['ma_v_30']=(data['ma_v_30'].max()-data['ma_v_30'])/(data['ma_v_30'].max()-data['ma_v_30'].min())
# data['ma_v_60']=(data['ma_v_60'].max()-data['ma_v_60'])/(data['ma_v_60'].max()-data['ma_v_60'].min())
# data['ma_v_90']=(data['ma_v_90'].max()-data['ma_v_90'])/(data['ma_v_90'].max()-data['ma_v_90'].min())
# data['ma_v_120']=(data['ma_v_120'].max()-data['ma_v_120'])/(data['ma_v_120'].max()-data['ma_v_120'].min())

# plt.plot(data['close'],c='k')
# plt.plot(data['ma_v_5'],c='r')
# plt.plot(data['ma_v_10'],c='r')
# plt.plot(data['ma_v_30'],c='r')
# plt.plot(data['ma_v_60'],c='g')
# plt.plot(data['ma_v_90'],c='r')
# plt.plot(data['ma_v_120'],c='r')

fig, ax1 = plt.subplots()

ax2 = ax1.twinx()    # mirror the ax1
ax1.plot(data['close'], 'k')
ax1.plot(data['ma30'], 'g')
# ax1.plot(data['ma120'], 'b')
# ax2.plot(data['ma_v_5'], 'r')
# ax2.plot(data['ma_v_10'], 'b')
# ax2.plot(data['ma_v_20'], 'g')
# ax2.plot(data['ma_v_30'], 'r')
# ax2.plot(data['ma_v_60'], 'g')
# ax2.plot(data['ma_v_90'], 'b')
ax2.plot(data['ma_v_120'], 'r')
# ax2.plot(data['ma_v_150'], 'c')


plt.show()

