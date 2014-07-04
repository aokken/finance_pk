
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension as ZTE



engine = create_engine('mysql://finance_pk:password@/finance_pk?unix_socket=/var/run/mysqld/mysqld.sock')
session_factory = sessionmaker(bind=engine, extension=ZTE())
DBSession = scoped_session(session_factory)


Base = declarative_base()