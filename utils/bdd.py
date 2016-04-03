__author__ = 'Vincent'
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)
from sqlalchemy.ext.declarative import declarative_base
import config
# from beans.session import Session


engine = create_engine(config.BDD_STRING_CONNECTION, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()


# def start_track_session():
#     session = Session()
#
#     # db_session.query(Session).filter()
#
#     return session

# Base.query = db_session.query_property()
# Base.metadata.create_all(engine)