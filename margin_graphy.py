import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pylab import axes
from data_download import data_download


start_date = '20110101'
end_date = '20151231'
margin_rzye=[]
margin_rqye=[]
rz_rate=[]
hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[10, 20, 30, 120])
for date in hs300_data['trade_date']:
    while True:
        try:
            margin=data_download().get_margin(date)
            margin_rzye.append(margin['rzye'].min())
            margin_rqye.append(margin['rqye'].min())
            rz_rate.append(margin['rzmre'].min()/margin['rzche'].min())
            print(date,margin['rzye'].min(),margin['rqye'].min(),margin['rzmre'].min()/margin['rzche'].min())
            time.sleep(0.5)
        except:
            time.sleep(5)
            continue
        else:
            break

fig, ax1 = plt.subplots()
ax2 = ax1.twinx()    # mirror the ax1


ax1.plot(hs300_data['trade_date'],hs300_data['close'], 'b-')
# ax2.plot(hs300_data['trade_date'],margin_rzye, 'r-')
# ax2.plot(hs300_data['trade_date'],margin_rqye, 'g-')
ax2.plot(hs300_data['trade_date'],rz_rate, 'r-')

plt.show()
