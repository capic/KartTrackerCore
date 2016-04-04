__author__ = 'Vincent'
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)
from sqlalchemy.ext.declarative import declarative_base
import config
from application.beans.session import Session
from datetime import date


engine = create_engine(config.BDD_STRING_CONNECTION, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()


def start_track_session(track_id):
    session = Session()

    qry = db_session.query(func.max(Session.id_day_session).label("max_id_day_session")).filter(Session.date_session == date.today()).filter(Session.track_id == track_id)
    res = qry.one()

    session.date_session = date.today()
    session.track_id = track_id
    session.name = "Session " + res.max_id_day_session + 1
    session.id_day_session = res.max_id_day_session + 1

    return session

# Base.query = db_session.query_property()
# Base.metadata.create_all(engine)