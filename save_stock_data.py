import pandas as pd
from data_download import data_download

path = 'Data/'
start_date = '20090101'
end_date = '20281231'

stocks = data_download().get_hs300()
# stocks = data_download().get_Astocks()
hs300_data = data_download().get_hs300_index(start_date, end_date, ma=[20, 30, 60, 120])
print(hs300_data)


for i in stocks.index[:]:
    code = stocks.ix[i, 'code']
    stock_data = data_download().get_stock_day_data(code, ma_list=[5, 10, 20, 30, 60, 90, 120],
                                                    start_date=start_date, end_date=end_date)
    if stock_data is not None:
        stock_data.to_csv(path+code+'.csv',index=False)
        print(path+code+'.csv')
