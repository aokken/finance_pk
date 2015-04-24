from sqlalchemy import Column, String, Enum, Float, Integer, Date, ForeignKey, func, \
                    orm
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
    
    __table_args__ = (UniqueConstraint('symbol', 'exchange', name='_symbol_exchange_constraint'),
                     )
    def __init__(self, symbol, name, exchange):
        self.symbol = symbol
        self.exchange = exchange
        self.name = name
        
    @staticmethod
    def get_security(session, symbol):
        """Static method to return a security.
           INPUT: ORM session, symbol
           OUTPUT: Security class object or raise name error if does not exist"""
        q = session.query(Security).filter(Security.symbol == symbol)
        if (q.count() > 0):
            return q.first()
        else:
            raise NameError("No security found for '{}'".format(symbol))
        
    def add_eod_history(self, session, history, update = False):
        for entry in history:
            self.add_eod_entry(session, entry, update)
        
    def add_eod_entry(self, session, observation, update = False):
        entry = None
        if (update == True):
            entry = self.get_eod_entry(observation['date'])
        
        if (entry is not None and update == True):
            entry.open = observation['open']
            entry.close = observation['close']
            entry.high = observation['high']
            entry.low = observation['low']
            entry.volume = observation['volume']
        else:
            entry = EOD_Entry(security_id = self.id,
                              date = observation['date'],
                              open = observation['open'],
                              close = observation['close'],
                              high = observation['high'],
                              low = observation['low'],
                              volume = observation['volume'])
            session.add(entry)
    
    def first_eod_entry(self):
        """Returns the earliest EOD entry from security"""
        return self.eod_entries.order_by(EOD_Entry.date).first()
    
    def last_eod_entry(self):
        """Returns the lastest EOD entry from security"""
        return self.eod_entries.order_by(EOD_Entry.date.desc()).first()
    
    def get_eod_entry(self, date):
        """Returns EOD entry of specified date"""
        return self.eod_entries.filter(EOD_Entry.date == date).first()
                
    def clear_eod_entries(self, session):
        """Delete all EOD entries"""
        eod_table = self.eod_entries.all()
        
        for entry in eod_table:
            session.delete(entry)
            
    def eod_entries_dates(self, start_date, end_date):
        """Get EOD entries between two dates"""
        return self.eod_entries. \
               filter(EOD_Entry.date >= start_date, EOD_Entry.date <= end_date).\
               order_by(EOD_Entry.date)
        
    
    
class SecurityMixin(object):
    """Abstract Mixin class for EOF_Entery, Stock_Transactions, ..., to 
    setup the relationship back to the security"""
    @declared_attr
    def id(cls):
        return Column(Integer, primary_key=True)
    
    @declared_attr
    def security_id(cls):
        return Column(Integer, 
                      ForeignKey("securities.id", onupdate="CASCADE", ondelete="CASCADE"), 
                      nullable=False)
    
    @declared_attr
    def security(cls):
        return relationship(Security, 
                            primaryjoin=lambda: Security.id==cls.security_id,
                            backref = backref(cls.__tablename__,
                                              uselist = True,
                                              single_parent=True,
                                              cascade="all, delete-orphan",
                                              passive_deletes=True,
                                              lazy='dynamic')   
                            )
        
    
class EOD_Entry(Base, SecurityMixin):
    __tablename__ = 'eod_entries'
    
    date = Column(Date, index=True)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
    
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
    

