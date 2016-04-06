__author__ = 'Vincent'
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)
from sqlalchemy.ext.declarative import declarative_base
import config
import unirest
from beans.track import Track


engine = create_engine(config.BDD_STRING_CONNECTION, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()


def update_from_central_database():
    response = unirest.get(config.REST_ADDRESS + 'tracks',
                           headers={"Accept": "application/json"})
    if response.code == 200:
        for json_object in response.body:
            track = Track()
            track.from_json(json_object)
            db_session.add(track)
            db_session.commit()

# Base.query = db_session.query_property()
# Base.metadata.create_all(engine)