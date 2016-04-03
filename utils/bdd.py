__author__ = 'Vincent'
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)
from sqlalchemy.ext.declarative import declarative_base
import config


engine = create_engine(config.BDD_STRING_CONNECTION, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()

# Base.query = db_session.query_property()
# Base.metadata.create_all(engine)