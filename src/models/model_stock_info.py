from sqlalchemy import Column, String, Enum, Float, Integer, Date, ForeignKey, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql.schema import UniqueConstraint

from models import Base


class Security(Base):
    """This is the basic class for each stock, bond. All price objects
    refer back to this table"""
    __tablename__ = 'securities'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(8), nullable=False)
    name = Column(String(50), nullable=False)
    exchange = Column(String(20), nullable=False)  
    eod_prices = relationship("EOD_Entry", backref=backref('securities'))
    splits = relationship("SplitsEntry", backref=backref('securities'))
    dividends = relationship("DividendEntry", backref=backref('securities'))
    
    
    __table_args__ = (UniqueConstraint('symbol', 'exchange', name='_symbol_exchange_constraint'),
                     )
    def __init__(self, symbol, name, exchange):
        self.symbol = symbol
        self.exchange = exchange
        self.name = name
        
    def add_eod_entry(self, session, observation):
        entry = EOD_Entry(security_id = self.id,
                          date = observation['date'],
                          open = observation['open'],
                          close = observation['close'],
                          high = observation['high'],
                          low = observation['low'])
        session.add(entry)
        
    def last_eod_entry_date(self, session):
        return session.query(self.eod_prices.date).\
                filter(self.eod_prices.date==func.max(self.eod_prices.date).select()).all
    
    
class SecurityMixin(object):
    """Abstract Mixin class for EOF_Entery, Stock_Transactions, ..., to 
    setup the relationship back to the security"""
    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True)
    
    @declared_attr
    def security_id(cls):
        return Column(Integer, ForeignKey("securities.id"), nullable=False)
    
    @declared_attr
    def security(cls):
        return relationship(Security, 
                            primaryjoin=lambda: Security.id==cls.security_id )
        
    
class EOD_Entry(Base, SecurityMixin):
    __tablename__ = 'eod_entries'
    
    date = Column(Date, index=True)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    
    __table_args__ = (UniqueConstraint('security_id', 'date', name='_security_date_constraint'),)
    
class SplitsEntry(Base, SecurityMixin):
    __tablename__ = 'split_entries'
    
    date = Column(Date, index=True)
    ratio = Column(Float, nullable=False)
    __table_args__ = (UniqueConstraint('security_id', 'date', name='_security_date_constraint'),)
    
class DividendEntry(Base, SecurityMixin):
    __tablename__ = 'dividend_entries'
    
    exdate = Column(Date, nullable=False)
    paydate = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    __table_args__ = (UniqueConstraint('security_id', 'exdate', name='_security_date_constraint'),)
    
# class Stock_Tr    UniqueConstraintansactions(Base, SecurityMixin):
#     __tablename__ = 'stock_transactions'
#     creation_date = Column(Date)
#     action = Column(Enum('BUY', 'SELL'), name='buy_sell')
#     shares = Column(Integer)
#     price = Column(Float)
    

