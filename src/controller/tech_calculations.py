'''
Created on Mar 1, 2015

@author: aaron
'''
from models.model_stock_info import Security, EOD_Entry
from models import DBSession
import talib
import numpy as np
from pandas import DataFrame, Series

talib_functions = talib.get_functions()
pattern_functions = talib.get_function_groups()['Pattern Recognition']

class Security_Frame(DataFrame):
    def __init__(self, symbol, start_date=None, end_date=None):
        if isinstance(symbol, Security):
            self.initalize_from_db(symbol, start_date, end_date)
        elif isinstance(symbol, basestring):
            session = DBSession()
            model = Security.get_security(session, symbol)
            self.initalize_from_db(model, start_date, end_date)
        else:
            raise TypeError("{} requires model.Security class or symbol name in constructor".
                            format(self.__class__.__name__))
    
    def initalize_from_db(self, model, start_date, end_date):
        if start_date is not None and end_date is not None:
            eods = model.eod_entries_dates(start_date, end_date) 
        else:
            eods = model.eod_entries.order_by(EOD_Entry.date)

        size = eods.count()
        arrays = {}
        dates = [0] * size
        arrays['open'] = np.ndarray(size)
        arrays['close'] = np.ndarray(size)
        arrays['low'] = np.ndarray(size)
        arrays['high'] = np.ndarray(size)
        arrays['volume'] = np.ndarray(size)
        
        for i in range(0, size):
            dates[i] = eods[i].date
            arrays['open'][i] = eods[i].open
            arrays['close'][i] = eods[i].close
            arrays['low'][i] = eods[i].low
            arrays['high'][i] = eods[i].high
            arrays['volume'][i] = eods[i].volume
        
        super(Security_Frame, self).__init__(data=arrays, index=dates)
        
        self.indicators = []
            
    
    def MA(self, samples=30, var='close'):
        MA = talib.MA(self.as_matrix([var])[:,0], samples)
        return MA
    
    def call_ohlc(self, func_name, *args, **kwargs):        
        if not func_name in talib_functions:
            raise Exception("'{}' is not a valid talib function".format(func_name))
        
        if hasattr(func_name, '__call__'):
            func = func_name
        else:
            func = getattr(talib, func_name)
        
        return func(self.open.values, 
                    self.high.values,
                    self.low.values,
                    self.close.values, *args, **kwargs)
        
    def call_hlc(self, func_name, *args, **kwargs):        
        if not func_name in talib_functions:
            raise Exception("'{}' is not a valid talib function".format(func_name))
        
        if hasattr(func_name, '__call__'):
            func = func_name
        else:
            func = getattr(talib, func_name)
        
        return func(self.high.values,
                    self.low.values,
                    self.close.values, *args, **kwargs)
        
    def call_hl(self, func_name, *args, **kwargs):        
        if not func_name in talib_functions:
            raise Exception("'{}' is not a valid talib function".format(func_name))
        
        if hasattr(func_name, '__call__'):
            func = func_name
        else:
            func = getattr(talib, func_name)
        
        return func(self.high.values,
                    self.low.values, *args, **kwargs)
    
    def check_all_patterns(self):
        for f in pattern_functions:
            Pattern(self, f)
            
class indicator(object):
    def __init__(self, frame):
        self.frame = frame
        
    def get_buy_sell_points(self):
        pass
    
    def __repr__(self):
        return "{}".format(self.name)
    
class ADX(indicator):
    """Calculate ADX"""
    def __init__(self, frame, timeperiod=14):
        super(ADX, self).__init__(frame)
        self.timeperiod = timeperiod
        self.name = "ADX{}".format(self.timeperiod)
        self.value = DataFrame({'adx': frame.call_hlc(talib.ADX, timeperiod=self.timeperiod), 
                                'di-': frame.call_hlc(talib.MINUS_DI, timeperiod=self.timeperiod),
                                'di+': frame.call_hlc(talib.PLUS_DI, timeperiod=self.timeperiod)},
                               index=frame.index)

class ADXR(indicator):
    """Average Directional Movement Index Rating"""
    def __init__(self, frame, timeperiod=14):
        super(ADXR, self).__init__(frame)
        self.timeperiod = timeperiod
        self.name = "ADXR{}".format(self.timeperiod)
        self.value = Series(frame.call_hlc(talib.ADXR, timeperiod=self.timeperiod),
                            index=frame.index)
        
class APO(indicator):
    """Absolute Price Oscillator"""
    def __init__(self, frame, fastperiod=12, slowperiod=26, matype=0):
        super(ADXR, self).__init__(frame)
        self.fastperiod = fastperiod
        self.slowperiod = slowperiod
        self.matype = matype
        self.name = "APO{}_{}_{}".format(self.matype, self.fastperiod, self.slowperiod)
        self.value = Series(talib.APO(frame['close'], 
                                      fastperiod=12, 
                                      slowperiod=26, 
                                      matype=0), index=frame.index)

class AROON(indicator):
    def __init__(self,frame, timeperiod=14):
        super(ADXR, self).__init__(frame)
        self.name = "AROON{}".format(timeperiod)
        up, down = frame.call_hl(talib.AROON, timeperiod=timeperiod)
        osc = frame.call_hl(talib.AROONOSC, timeperiod=timeperiod)
        
        self.value = DataFrame({'up': up,
                                'down': down,
                                'osc': osc}, index=frame.index)


class Pattern(indicator):
    """Pattern matching functions"""
    def __init__(self, frame, pattern_name, *args, **kwargs):        
        if not pattern_name in pattern_functions:
            raise Exception("'{}' is not a valid pattern function".format(pattern_name))
        
        super(Pattern, self).__init__(frame)
        
        self.name = pattern_name
        ser = Series(frame.call_ohlc(pattern_name, *args, **kwargs), 
                     index=frame.index)
        self.value = ser[ser!=0]
        
    def bull_matches(self):
        col = self.value
        col = col[col > 0]
        col.index.get_values()
        
    def bear_matches(self):
        col = self.value
        col = col[col < 0]
        col.index.get_values()
        
        
if __name__ == "__main__":
    sec = Security_Frame('FDX')
    sec.check_all_patterns()
