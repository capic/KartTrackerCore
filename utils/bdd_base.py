__author__ = 'Vincent'
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
import config


# engine = create_engine(config.BDD_STRING_CONNECTION, convert_unicode=True, echo=True)
engine = create_engine(config.BDD_STRING_CONNECTION, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))

Base = declarative_base()

# ############# TRACK ###########


class Track(Base):
    __tablename__ = 'track'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    session = relationship("Session")

    def __repr__(self):
        return '{id: ' + str(self.id) + ', name: ' + str(self.name) + '}'

    def from_json(self, json):
        self.id = json['id']
        self.name = json['name']


# ############ SESSION ############


class Session(Base):
    __tablename__ = 'session'
    id = Column(Integer, primary_key=True)
    id_day_session = Column(Integer)
    date_session = Column(Date)
    name = Column(String)
    start_time = Column(Time)
    end_time = Column(Time)

    gps_datas = relationship("GPSData")
    track_id = Column(Integer, ForeignKey('track.id'))

    def __repr__(self):
        return '{id: ' + str(self.id) + ', id_day_session: ' + str(self.id_day_session) + ', date_session: ' + str(
            self.date_session) + ', name: ' + str(self.name) + ', start_time: ' + str(
            self.start_time) + ', end_time: ' + str(self.end_time) + ', track_id: ' + str(
            self.track_id) + '}'

# ############### GPS DATA ##############


class GPSData(Base):
    __tablename__ = 'gps_data'
    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    date_time = Column(String)

    session_id = Column(Integer, ForeignKey('session.id'))

    def __repr__(self):
        return '{id: ' + str(self.id) + ', latitude: ' + str(self.latitude) + ', longitude: ' + str(
            self.longitude) + ', speed: ' + str(self.speed) + ', date_time: ' + str(
            self.date_time) + ', session_id: ' + str(self.session_id) + '}'

# Base.query = db_session.query_property()
Base.metadata.create_all(engine)