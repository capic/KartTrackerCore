__author__ = 'Vincent'
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from session import Session
from utils.bdd import Base, engine


class GPSData(Base):
    __tablename__ = 'GpsDatas'
    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    date_time = Column(String)

    session_id = Column(Integer, ForeignKey('Sessions.id'))
    session = relationship(Session)

    def __repr__(self):
        return '{id: ' + str(self.id) + ', latitude: ' + str(self.latitude) + ', longitude: ' + str(
            self.longitude) + ', speed: ' + str(self.speed) + ', date_time: ' + str(
            self.date_time) + ', session_id: ' + str(self.session_id) + '}'


Base.metadata.create_all(engine)
