__author__ = 'Vincent'
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy import ForeignKey
from utils.bdd_base import Base, engine
from sqlalchemy.orm import relationship


class GPSData(Base):
    __tablename__ = 'gps_data'
    id = Column(Integer, primary_key=True)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    date_time = Column(String)

    session_id = Column(Integer, ForeignKey('session.id'))
    session = relationship("Session", back_populates="gps_data")

    # def __repr__(self):
    #     return '{id: ' + str(self.id) + ', latitude: ' + str(self.latitude) + ', longitude: ' + str(
    #         self.longitude) + ', speed: ' + str(self.speed) + ', date_time: ' + str(
    #         self.date_time) + ', session_id: ' + str(self.session_id) + '}'

Base.metadata.create_all(engine)
