import ystockquote as ysq
import talib
import numpy as np
from datetime import date

from collections import OrderedDict

class stock_calculation(object):
    def __init__(self, symbol, start_date):
        self.symbol = symbol
        self.load_eod_historical_data(start_date)
    
    def load_eod_historical_data(self, start_date):
        quotes = ysq.get_historical_prices(self.symbol,
                                           date.today().isoformat(),
                                           start_date.isoformat())

        l = len(quotes.keys())
        self.arr_open = np.empty(l)
        self.arr_close = np.empty(l)
        self.arr_high = np.empty(l)
        self.arr_low = np.empty(l) 
        self.arr_vol = np.empty(l)  
        
        dates = {}
        for d in quotes.keys():
            [year, month, day] = d.split('-')
            dates[d] = date(year, month, day)
            
        ordered = OrderedDict(sorted(dates.items(), key=lambda x: x[1]))

        i = 0
        for key, d in ordered:
            q = quotes[key]
            self.arr_open[i] = q["Open"]
            self.arr_close[i] = q["Adj Close"]
            self.arr_high[i] = q["High"]
            self.arr_low[i] = q["Low"]
            self.arr_vol[i] = q["Volume"]
            i=i+1
        
if __name__ == '__main__':
    pass
