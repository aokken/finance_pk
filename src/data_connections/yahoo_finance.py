'''
Created on Jan 27, 2014

@author: aaron
'''

from datetime import date
from urllib2 import Request, urlopen
from urllib import urlencode

# TODO: Put these in a database some day
options = {
        'AfterHoursChangeRealtime' : {'description' : 'After Hours Change (Realtime)', 'chars' : 'c8' },
        'AnnualizedGain    ' : {'description' : 'Annualized Gain', 'chars' : 'g3' },
        'Ask' : {'description' : 'Ask', 'chars' : 'a0' },
        'AskRealtime' : {'description' : 'Ask (Realtime)', 'chars' : 'b2' },
        'AskSize' : {'description' : 'Ask Size', 'chars' : 'a5' },
        'AverageDailyVolume' : {'description' : 'Average Daily Volume', 'chars' : 'a2' },
        'Bid' : {'descr    ption' : 'Bid', 'chars' : 'b0' },
        'BidRealtime' : {'description' : 'Bid (Realtime)', 'chars' : 'b3' },
        'BidSize' : {'description' : 'Bid Size', 'chars' : 'b6' },
        'BookValuePerShare' : {'description' : 'Book Value Per Share', 'chars' : 'b4' },
        'Change' : {'description' : 'Change', 'chars' : 'c1' },
        'Change_ChangeInPercent'  : {'description' : 'Change In Percent', 'chars' : 'c0'},
        'ChangeFromFiftydayMovingAverage' : {'description' : 'Change From Fiftyday Moving Average', 'chars' : 'm7' },
        'ChangeFromTwoHundreddayMovingAverage' : {'description' : 'Change From Two Hundredday Moving Average', 'chars' : 'm5' },
        'ChangeFromYearHigh' : {'description' : 'Change From Year High', 'chars' : 'k4' },
        'ChangeFromYearLow' : {'description' : 'Change From Year Low', 'chars' : 'j5' },
        'ChangeInPercent' : {'description' : 'Change In Percent', 'chars' : 'p2' },
        'ChangeInPercentRealtime' : {'description' : 'Change In Percent (Realtime)', 'chars' : 'k2' },
        'ChangeRealtime' : {'description' : 'Change (Realtime)', 'chars' : 'c6' },
        'Commission' : {'description' : 'Commission', 'chars' : 'c3' },
        'Currency' : {'description' : 'Currency', 'chars' : 'c4' },
        'DaysHigh' : {'description' : 'Days High', 'chars' : 'h0' },
        'DaysLow' : {'description' : 'Days Low', 'chars' : 'g0' },
        'DaysRange' : {'description' : 'Days Range', 'chars' : 'm0' },
        'DaysRangeRealtime' : {'description' : 'Days Range (Realtime)', 'chars' : 'm2' },
        'DaysValueChange' : {'description' : 'Days Value Change', 'chars' : 'w1' },
        'DaysValueChangeRealtime' : {'description' : 'Days Value Change (Realtime)', 'chars' : 'w4' },
        'DividendPayDate' : {'description' : 'Dividend Pay Date', 'chars' : 'r1' },
        'TrailingAnnualDividendYield' : {'description' : 'Trailing Annual Dividend Yield', 'chars' : 'd0' },
        'TrailingAnnualDividendYieldInPercent' : {'description' : 'Trailing Annual Dividend Yield In Percent', 'chars' : 'y0' },
        'DilutedEPS' : {'description' : 'Diluted E P S', 'chars' : 'e0' },
        'EBITDA' : {'description' : 'E B I T D A', 'chars' : 'j4' },
        'EPSEstimateCurrentYear' : {'description' : 'E P S Estimate Current Year', 'chars' : 'e7' },
        'EPSEstimateNextQuarter' : {'description' : 'E P S Estimate Next Quarter', 'chars' : 'e9' },
        'EPSEstimateNextYear' : {'description' : 'E P S Estimate Next Year', 'chars' : 'e8' },
        'ExDividendDate' : {'description' : 'Ex Dividend Date', 'chars' : 'q0' },
        'FiftydayMovingAverage' : {'description' : 'Fiftyday Moving Average', 'chars' : 'm3' },
        'SharesFloat' : {'description' : 'Shares Float', 'chars' : 'f6' },
        'HighLimit' : {'description' : 'High Limit', 'chars' : 'l2' },
        'HoldingsGain' : {'description' : 'Holdings Gain', 'chars' : 'g4' },
        'HoldingsGainPercent' : {'description' : 'Holdings Gain Percent', 'chars' : 'g1' },
        'HoldingsGainPercentRealtime' : {'description' : 'Holdings Gain Percent (Realtime)', 'chars' : 'g5' },
        'HoldingsGainRealtime' : {'description' : 'Holdings Gain (Realtime)', 'chars' : 'g6' },
        'HoldingsValue' : {'description' : 'Holdings Value', 'chars' : 'v1' },
        'HoldingsValueRealtime' : {'description' : 'Holdings Value (Realtime)', 'chars' : 'v7' },
        'LastTradeDate' : {'description' : 'Last Trade Date', 'chars' : 'd1' },
        'LastTradePriceOnly' : {'description' : 'Last Trade Price Only', 'chars' : 'l1' },
        'LastTradeRealtimeWithTime' : {'description' : 'Last Trade (Realtime) With Time', 'chars' : 'k1' },
        'LastTradeSize' : {'description' : 'Last Trade Size', 'chars' : 'k3' },
        'LastTradeTime' : {'description' : 'Last Trade Time', 'chars' : 't1' },
        'LastTradeWithTime' : {'description' : 'Last Trade With Time', 'chars' : 'l0' },
        'LowLimit' : {'description' : 'Low Limit', 'chars' : 'l3' },
        'MarketCapitalization' : {'description' : 'Market Capitalization', 'chars' : 'j1' },
        'MarketCapRealtime' : {'description' : 'Market Cap (Realtime)', 'chars' : 'j3' },
        'MoreInfo' : {'description' : 'More Info', 'chars' : 'i0' },
        'Name' : {'description' : 'Name', 'chars' : 'n0' },
        'Notes' : {'description' : 'Notes', 'chars' : 'n4' },
        'OneyrTargetPrice' : {'description' : 'Oneyr Target Price', 'chars' : 't8' },
        'Open' : {'description' : 'Open', 'chars' : 'o0' },
        'OrderBookRealtime' : {'description' : 'Order Book (Realtime)', 'chars' : 'i5' },
        'PEGRatio' : {'description' : 'P E G Ratio', 'chars' : 'r5' },
        'PERatio' : {'description' : 'P E Ratio', 'chars' : 'r0' },
        'PERatioRealtime' : {'description' : 'P E Ratio (Realtime)', 'chars' : 'r2' },
        'PercentChangeFromFiftydayMovingAverage' : {'description' : 'Percent Change From Fiftyday Moving Average', 'chars' : 'm8' },
        'PercentChangeFromTwoHundreddayMovingAverage' : {'description' : 'Percent Change From Two Hundredday Moving Average', 'chars' : 'm6' },
        'ChangeInPercentFromYearHigh' : {'description' : 'Change In Percent From Year High', 'chars' : 'k5' },
        'PercentChangeFromYearLow' : {'description' : 'Percent Change From Year Low', 'chars' : 'j6' },
        'PreviousClose' : {'description' : 'Previous Close', 'chars' : 'p0' },
        'PriceBook' : {'description' : 'Price Book', 'chars' : 'p6' },
        'PriceEPSEstimateCurrentYear' : {'description' : 'Price E P S Estimate Current Year', 'chars' : 'r6' },
        'PriceEPSEstimateNextYear' : {'description' : 'Price E P S Estimate Next Year', 'chars' : 'r7' },
        'PricePaid' : {'description' : 'Price Paid', 'chars' : 'p1' },
        'PriceSales' : {'description' : 'Price Sales', 'chars' : 'p5' },
        'Revenue' : {'description' : 'Revenue', 'chars' : 's6' },
        'SharesOwned' : {'description' : 'Shares Owned', 'chars' : 's1' },
        'SharesOutstanding' : {'description' : 'Shares Outstanding', 'chars' : 'j2' },
        'ShortRatio' : {'description' : 'Short Ratio', 'chars' : 's7' },
        'StockExchange' : {'description' : 'Stock Exchange', 'chars' : 'x0' },
        'Symbol' : {'description' : 'Symbol', 'chars' : 's0' },
        'TickerTrend' : {'description' : 'Ticker Trend', 'chars' : 't7' },
        'TradeDate' : {'description' : 'Trade Date', 'chars' : 'd2' },
        'TradeLinks' : {'description' : 'Trade Links', 'chars' : 't6' },
        'TradeLinksAdditional' : {'description' : 'Trade Links Additional', 'chars' : 'f0' },
        'TwoHundreddayMovingAverage' : {'description' : 'Two Hundredday Moving Average', 'chars' : 'm4' },
        'Volume' : {'description' : 'Volume', 'chars' : 'v0' },
        'YearHigh' : {'description' : 'Year High', 'chars' : 'k0' },
        'YearLow' : {'description' : 'Year Low', 'chars' : 'j0' },
        'YearRange' : {'description' : 'Year Range', 'chars' : 'w0' }}
    
class Yahoo_Finance(object):
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        
    def _request(self, symbol, stat):
        url = 'http://finance.yahoo.com/d/quotes.csv?s=%s&f=%s' % (symbol, stat)
        req = Request(url)
        resp = urlopen(req)
        return str(resp.read().decode('utf-8').strip())
        
    def get_stats(self, symbol, *args):
        query = ''
        
        for a in args:
            if options.has_key(a):
                query = query + options[a]['chars']
            else:
                raise Exception("Requested key, '%s', not defined!"%a)
                
        values = self._request(symbol, query).split(',')
        if (values[1] == '"N/A"'):
            raise Exception("Yahoo returned N/A; check symbol %s"%symbol)
        
        return {attrib: val for attrib, val in zip(args, values)}
            
    def get_eod_prices(self, symbol, start_date, end_date):
        """
        Get historical prices for the given ticker symbol.
        Date format is 'YYYY-MM-DD'

        Returns a nested dictionary (dict of dicts).
        outer dict keys are dates ('YYYY-MM-DD')
        """
        start = start_date.isoformat()
        end = end_date.isoformat()
        params = urlencode({
                            's': symbol,
                            'a': int(start[5:7]) - 1,
                            'b': int(start[8:10]),
                            'c': int(start[0:4]),
                            'd': int(end[5:7]) - 1,
                            'e': int(end[8:10]),
                            'f': int(end[0:4]),
                            'g': 'd',
                            'ignore': '.csv',
                            })
        
        url = 'http://ichart.yahoo.com/table.csv?%s' % params
        req = Request(url)
        resp = urlopen(req)
        content = str(resp.read().decode('utf-8').strip())
        daily_data = content.splitlines()
        hist = []
        keys = daily_data[0].split(',')
        keys = map(lambda x: x.lower(), keys)
        
        for day in daily_data[1:]:
            day_data = day.split(',')
            #[y, m, d] = day_data[0].split('-')
            #da = date(int(y), int(m), int(d))
            ymd = map(lambda x: int(x), day_data[0].split('-'))
            da = date(*ymd)
            hist.append({keys[0]: da,
                         keys[1]: day_data[1],
                         keys[2]: day_data[2],
                         keys[3]: day_data[3],
                         keys[4]: day_data[4],
                         keys[5]: day_data[5],
                         keys[6]: day_data[6]})

        return hist

        
        
        
if __name__ == "__main__":
    y = Yahoo_Finance()
    r = y.get_stats('GOOG', 'YearRange', 'DilutedEPS')
    #r = y.get_eod_prices('GOOG', date(2014,1,1), date.today())
    print r
    pass
        
