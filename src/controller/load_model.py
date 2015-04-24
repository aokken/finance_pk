'''
Created on Jan 31, 2014

@author: aaron
'''
import threading
from threading import Thread
from sqlalchemy import and_
from sqlalchemy.exc import DBAPIError
from models.model_stock_info import Security
from models import DBSession
from data_connections.yahoo_finance import Yahoo_Finance
from US_trading_calandar import TradingDays
from datetime import date, datetime

yahoo = Yahoo_Finance()
calendar = TradingDays()            

def load_security(symbol, session=None):
    if session is None:
        session = DBSession()
        
    try:
        session = DBSession()
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
       

def load_history(symbol, date_range, session=None):
    if session is None:
        session = DBSession()
    
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
    
def update_history (symbol, d = date.today()):
    session = DBSession()
    
    if not isinstance(d, date):
        raise TypeError('date_range must be type date')
    
    latest_day = calendar.last_trading_day()
    
    if not isinstance(symbol, Security):
        symbol = Security.get_security(session, symbol)
    
    hist_last_day = symbol.last_eod_entry().date
    
    if (hist_last_day == latest_day):
        print "{} is already up to date".format(symbol.name)
    else:
        load_history(symbol, (hist_last_day, latest_day), session=session)

    

if __name__ == "__main__":
    symbols = ['GOOG', 'MSFT', 'FDX', 'SOXL']
    
    #===========================================================================
    # for sym in symbols:
    #     n = "load_security-{}".format(sym)
    #     th = Thread(target=load_security, args=(sym,), name=n)
    #     th.start()
    #     
    # for th in threading.enumerate():
    #     if th == threading.current_thread(): continue
    #     th.join()
    #     print "Joined thread for load_security {}".format(th.name)
    # 
    # for sym in symbols:
    #     th = Thread(target=load_history, args=(sym, (date(2014,1,1), date.today())))
    #     th.start()
    #     
    # for th in threading.enumerate():
    #     if th == threading.current_thread(): continue
    #     th.join()
    #===========================================================================
    

    #===========================================================================
    # test_obs = {'date': date(2015,1,30),
    #             'open': 10.2,
    #             'close': 30.3,
    #             'high': 34.4,
    #             'low': 10}
    #===========================================================================

    #stock.add_eod_entry(session, test_obs, True)
    