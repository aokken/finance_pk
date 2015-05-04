'''
Created on Mar 1, 2015

@author: aaron
'''
from models.model_stock_info import Security, EOD_Entry
from models import DBSession
import talib
import numpy as np
from pandas import DataFrame, Series
from decorators import decorate_date_args
from US_trading_calandar import TradingDays
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import colorConverter
import matplotlib.ticker as ticker

talib_functions = talib.get_functions()
pattern_functions = talib.get_function_groups()['Pattern Recognition']

class Security_Frame(DataFrame):
    @decorate_date_args('start_date', 'end_date')
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
            
    def __repr__(self):
        rep = "{} - {}\n".format(self.model.symbol, self.model.exchange)
        return rep + super(Security_Frame, self).__repr__()
    
    def initalize_from_db(self, model, start_date, end_date):
        eods = model.eod_entries_dates(start_date=start_date, end_date=end_date) 

        size = eods.count()
        arrays = {}
        dates = [0] * size
        arrays['open'] = np.ndarray(size)
        arrays['close'] = np.ndarray(size)
        arrays['low'] = np.ndarray(size)
        arrays['high'] = np.ndarray(size)
        arrays['volume'] = np.ndarray(size)
        
        for i in range(0, size):
            eod = eods[i]
            dates[i] = eod.date
            arrays['open'][i] = eod.open
            arrays['close'][i] = eod.close
            arrays['low'][i] = eod.low
            arrays['high'][i] = eod.high
            arrays['volume'][i] = eod.volume
        
        super(Security_Frame, self).__init__(data=arrays, index=dates)
        self.model = model
        self.calendar = TradingDays(start_date=dates[0])
        self.indicators = {}
            
    def __del__(self):
        for ind in self.indicators.itervalues():
            del ind
        
    def MA(self, samples=30, var='close'):
        MA = talib.MA(self.as_matrix([var])[:,0], samples)
        return MA
    
    def check_all_patterns(self):
        return [Pattern(self, f) for f in pattern_functions]
            
    def register_indicator(self, ind):
        if ind.name in self.indicators:
            raise ValueError("{} already exists".format(ind.name))
        
        self.indicators[ind.name] = ind
        
    def deregister_indicator(self,ind):
        if ind.name in self.indicators:
            del self.indicators[ind.name]
        else:
            raise ValueError("{} is not registered".format(ind.name))
        
    def candlestick_plot(self, ax, width=0.75, colorup='g', colordown='r',
                 alpha=1):   
            
        delta = width/ 2.
        barVerts = [((i - delta, open),
                    (i - delta, close),
                    (i + delta, close),
                    (i + delta, open))
                    for i, open, close in zip(xrange(len(self['open'])), self['open'], self['close'])
                    if open != -1 and close != -1]

        rangeSegments = [((i, low), (i, high))
                        for i, low, high in zip(xrange(len(self['low'])), self['low'], self['high'])
                        if low != -1]

        r, g, b = colorConverter.to_rgb(colorup)
        colorup = r, g, b, alpha
        r, g, b = colorConverter.to_rgb(colordown)
        colordown = r, g, b, alpha
        colord = {True: colorup,
                  False: colordown,
                  }       
        colors = [colord[open < close]
                  for open, close in zip(self['open'], self['close'])
                  if open != -1 and close != -1]

        assert(len(barVerts) == len(rangeSegments))

        useAA = 0,  # use tuple here
        lw = 0.5,   # and here
        rangeCollection = LineCollection(rangeSegments,
                                         colors=colors,
                                         linewidths=lw,
                                         antialiaseds = useAA,
                                        )

                                   
        barCollection = PolyCollection(barVerts,
                                       facecolors=colors,
                                       edgecolors=colors,
                                       antialiaseds=useAA,
                                       linewidths=lw)

        minx, maxx = 0, len(rangeSegments)
        miny = min([low for low in self['low'] if low != -1])
        maxy = max([high for high in self['high'] if high != -1])

        corners = (minx, miny), (maxx, maxy)
        ax.update_datalim(corners)
        ax.autoscale_view()

        # add these last
        ax.add_collection(barCollection)
        ax.add_collection(rangeCollection)

        ax.xaxis.set_major_formatter(ticker.FuncFormatter(PlotDateAxis(self.calendar)))
        ax.figure.autofmt_xdate()
        return rangeCollection, barCollection
    
class PlotDateAxis(object):
    def __init__(self, index):
        self.index = index
        
    def __call__(self, x, pos=None):
        x = int(x)
        return self.index[x].date().isoformat()
            
class Indicator(object):
    def __init__(self, frame, name):
        self.frame = frame
        self.name = name
        frame.register_indicator(self)
        
    def __del__(self):
        self.frame.deregister_indicator(self)
        
    def call_ohlc(self, func_name, *args, **kwargs):        
        if hasattr(func_name, '__call__'):
            func = func_name
        else:
            if not func_name in talib_functions:
                raise Exception("'{}' is not a valid talib function".format(func_name))
            func = getattr(talib, func_name)
        
        return func(self.frame.open.values, 
                    self.frame.high.values,
                    self.frame.low.values,
                    self.frame.close.values, *args, **kwargs)
        
    def call_hlc(self, func_name, *args, **kwargs):        
        if hasattr(func_name, '__call__'):
            func = func_name
        else:
            if not func_name in talib_functions:
                raise Exception("'{}' is not a valid talib function".format(func_name))
            func = getattr(talib, func_name)
        
        return func(self.frame.high.values,
                    self.frame.low.values,
                    self.frame.close.values, *args, **kwargs)
        
    def call_hl(self, func_name, *args, **kwargs):    
        """Call func_name with frames high, low. func_name must be name of talib function or
        a callable itself"""
        if hasattr(func_name, '__call__'):
            func = func_name
        else:
            if not func_name in talib_functions:
                raise Exception("'{}' is not a valid talib function".format(func_name))
            func = getattr(talib, func_name)
        
        return func(self.frame.high.values,
                    self.frame.low.values, *args, **kwargs)
        
    def plot(self, ax=None, **kwargs):
        if ax is None:
            from matplotlib.pyplot import subplots
            fig, ax = subplots()
        
        plt = self.value.plot(ax=ax, use_index=False)
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(PlotDateAxis(self.frame.calendar)))
        ax.figure.autofmt_xdate()
        return plt
        
    def get_buy_sell_points(self):
        pass
    
    def __repr__(self):
        return "{} - {}\n".format(self.frame.model.symbol, self.name) + self.value.__repr__()
    
class ADX(Indicator):
    """Calculate ADX"""
    def __init__(self, frame, timeperiod=14):
        super(ADX, self).__init__(frame, "ADX_timeperiod{}".format(timeperiod))
        
        self.value = DataFrame({'adx': self.call_hlc(talib.ADX, timeperiod=timeperiod), 
                                'di-': self.call_hlc(talib.MINUS_DI, timeperiod=timeperiod),
                                'di+': self.call_hlc(talib.PLUS_DI, timeperiod=timeperiod)},
                               index=frame.index)

class ADXR(Indicator):
    """Average Directional Movement Index Rating"""
    def __init__(self, frame, timeperiod=14):
        super(ADXR, self).__init__(frame, "ADXR_timeperiod{}".format(timeperiod))
        self.value = Series(self.call_hlc(talib.ADXR, timeperiod=timeperiod),
                            index=frame.index)
        
class APO(Indicator):
    """Absolute Price Oscillator"""
    def __init__(self, frame, fastperiod=12, slowperiod=26, matype=0):
        super(APO, self).__init__(frame, 
                                  "APO_matype{}_fastperiod{}_slowperiod{}".format(matype, 
                                                                                  fastperiod, 
                                                                                  slowperiod))

        self.value = Series(talib.APO(frame['close'], 
                                      fastperiod=12, 
                                      slowperiod=26, 
                                      matype=0), index=frame.index)

class AROON(Indicator):
    def __init__(self,frame, timeperiod=14):
        super(AROON, self).__init__(frame, "AROON_timeperiod{}".format(timeperiod))
        
        up, down = self.call_hl(talib.AROON, timeperiod=timeperiod)
        osc = self.call_hl(talib.AROONOSC, timeperiod=timeperiod)

        self.value = DataFrame({'up': up,
                                'down': down,
                                'osc': osc}, index=frame.index)


class Pattern(Indicator):
    """Pattern matching functions"""
    def __init__(self, frame, pattern_name, *args, **kwargs):        
        if not pattern_name in pattern_functions:
            raise Exception("'{}' is not a valid pattern function".format(pattern_name))
        
        super(Pattern, self).__init__(frame,"PATTERN_{}".format(pattern_name))
    
        ser = Series(self.call_ohlc(pattern_name, *args, **kwargs), 
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
        
def cross(series, cross=0, direction='cross'):
    """
    Given a Series returns all the index values where the data values equal 
    the 'cross' value. 

    Direction can be 'rising' (for rising edge), 'falling' (for only falling 
    edge), or 'cross' for both edges
    """
    # Find if values are above or bellow yvalue crossing:
    above=series.values > cross
    below=np.logical_not(above)
    left_shifted_above = above[1:]
    left_shifted_below = below[1:]

    # Find indexes on left side of crossing point
    if direction == 'rising':
        idxs = (left_shifted_above & below[0:-1]).nonzero()[0]
    elif direction == 'falling':
        idxs = (left_shifted_below & above[0:-1]).nonzero()[0]
    else:
        rising = left_shifted_above & below[0:-1]
        falling = left_shifted_below & above[0:-1]
        idxs = (rising | falling).nonzero()[0]
        
    return idxs+1

if __name__ == "__main__":
    sec = Security_Frame('FDX', start_date='2015/02/01')
    from matplotlib import pyplot as plt
    fig, ax = plt.subplots()
    sec.candlestick_plot(ax)
    plt.show()
    adx = AROON(sec)
    sec.check_all_patterns()
