__author__ = 'Vincent'
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from session import Session
from utils.bdd_base import Base, engine
import json


class GPSData(Base):
    __tablename__ = 'GpsData'
    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    date_time = Column(String)

    session_id = Column(Integer, ForeignKey('Session.id'))
    session = relationship(Session)

    def __repr__(self):
        return '{id: ' + str(self.id) + ', latitude: ' + str(self.latitude) + ', longitude: ' + str(
            self.longitude) + ', speed: ' + str(self.speed) + ', date_time: ' + str(
            self.date_time) + ', session_id: ' + str(self.session_id) + '}'

    def to_json(self):
        return {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'speed': self.speed,
            'date_time': self.date_time,
            'session_id': self.session_id,
            'session': self.session.to_json() if self.session is not None else None
        }

Base.metadata.create_all(engine)
