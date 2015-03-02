'''
Created on Jan 31, 2014

@author: aaron
'''
from sqlalchemy import and_
from sqlalchemy.exc import DBAPIError
from models.model_stock_info import Security
from models import DBSession
from data_connections.yahoo_finance import Yahoo_Finance
from US_trading_calandar import TradingDays
from datetime import date, datetime

yahoo = Yahoo_Finance()
calendar = TradingDays()

def load_security(session, symbol):
    try:
        stats = yahoo.get_stats(symbol, 'Name', 'StockExchange')
        security = Security(symbol, stats['Name'], stats['StockExchange'])
        session.add(security)
        session.commit()
    except DBAPIError as err:
        session.rollback()
        security = Security.get_security(session, symbol)
        
        if security is None:
            raise err
    except:
        session.rollback()
        raise
    
    return security
       

def load_history(session, symbol, date_range):
    for d in date_range:
        if not isinstance(d, date):
            raise TypeError('date_range must be type date')
            
    if not isinstance(symbol, Security):
        symbol = Security.get_security(session, symbol)

    
    try:
        hist = yahoo.get_eod_prices(symbol.symbol, date_range[0], date_range[1])
        symbol.add_eod_history(session, hist, True)
    
        session.commit()
    except DBAPIError as err:
        session.rollback()
        print "Error updating database({})".format(err)
    except:
        raise
    
def update_history(session, symbol, d = date.today()):
    if not isinstance(d, date):
        raise TypeError('date_range must be type date')
    
    latest_day = calendar.last_trading_day()
    
    if not isinstance(symbol, Security):
        symbol = Security.get_security(session, symbol)
        
    hist_last_day = symbol.last_eod_entry().date
    
    load_history(session, symbol, (hist_last_day, latest_day))

    

if __name__ == "__main__":
    session = DBSession();
    
    for sym in ('GOOG', 'MSFT', 'FDX', 'SOXL'):
        try:
            sec = load_security(session, sym)
            load_history(session, sym, (date(2014,1,1), date.today()))
        except Exception as e:
            session.rollback()
            print "Error occurred in load_stock '{}': {}".format(sym, e)

    test_obs = {'date': date(2015,1,30),
                'open': 10.2,
                'close': 30.3,
                'high': 34.4,
                'low': 10}

    #stock.add_eod_entry(session, test_obs, True)
    