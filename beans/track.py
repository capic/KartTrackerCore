__author__ = 'Vincent'
from sqlalchemy import Column, Integer, String
from utils.bdd import Base, engine


class Track(Base):
    __tablename__ = 'Tracks'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return '{id: ' + str(self.id) + ', name: ' + str(self.name) + '}'

Base.metadata.create_all(engine)