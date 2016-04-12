__author__ = 'Vincent'
from sqlalchemy import Column, Integer, String, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from utils.bdd_base import Base, engine


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

    # def __repr__(self):
    #     return '{id: ' + str(self.id) + ', id_day_session: ' + str(self.id_day_session) + ', date_session: ' + str(
    #         self.date_session) + ', name: ' + str(self.name) + ', start_time: ' + str(
    #         self.start_time) + ', end_time: ' + str(self.end_time) + ', track_id: ' + str(
    #         self.track_id) + '}'

# Base.metadata.create_all(engine)


