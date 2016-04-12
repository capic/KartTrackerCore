__author__ = 'Vincent'
from sqlalchemy import Column, Integer, String
from utils.bdd_base import Base, engine
from sqlalchemy.orm import relationship


class Track(Base):
    __tablename__ = 'track'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    session = relationship("Session")

    def from_json(self, json):
        self.id = json['id']
        self.name = json['name']

    def __repr__(self):
        return '{id: ' + str(self.id) + ', name: ' + str(self.name) + '}'

Base.metadata.create_all(engine)