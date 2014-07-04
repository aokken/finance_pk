'''
Created on Jan 26, 2014

@author: aaron
'''
from models import Base, model_stock_info
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
    
if __name__ == '__main__':
    engine = create_engine('mysql://finance_pk:password@/finance_pk?unix_socket=/var/run/mysqld/mysqld.sock')

    Session = sessionmaker(bind=engine)
    session = Session()
    
    Base.metadata.create_all(engine)
    

