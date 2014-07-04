'''
Created on Jan 31, 2014

@author: aaron
'''
from sqlalchemy import and_

from models.model_stock_info import Security
from models import DBSession
from data_connections.yahoo_finance import Yahoo_Finance
from trading_calandar import TradingDays

yahoo = Yahoo_Finance()
calendar = TradingDays()

def load_stock(session, symbol):
    stats = yahoo.get_stats(symbol, 'Name', 'StockExchange')
    q = session.query(Security).filter(and_(Security.symbol == symbol, 
                                            Security.exchange == stats['StockExchange'])
                                       ).count()
    
    if (q == 0):
        security = Security(symbol, stats['Name'], stats['StockExchange'])
        session.add(security)
        session.commit()
    else:
        # TODO: Add logging that the stock already exists    
        pass
    
def get_history():
    pass

if __name__ == "__main__":
    
    load_stock(DBSession(), 'GOOG')


