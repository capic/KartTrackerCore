__author__ = 'Vincent'
from sqlalchemy import Column, Integer, String, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from track import Track
from utils.bdd import Base, engine


class Session(Base):
    __tablename__ = 'Sessions'
    id_day_session = Column(Integer, primary_key=True)
    date = Column(Date, primary_key=True)
    name = Column(String)
    start_time = Column(Time)
    end_time = Column(Time)

    track_id = Column(Integer, ForeignKey('Tracks.id'))
    track = relationship(Track)

    def __repr__(self):
        return '{id: ' + str(self.id) + ', name: ' + str(self.name) + ', start_date_time: ' + str(
            self.start_date_time) + ', end_date_time: ' + str(self.end_date_time) + ', track_id: ' + str(
            self.track_id) + '}'

# Track.sessions = relationship("Session", order_by=Session.id, back_populates="track")
Base.metadata.create_all(engine)


