__author__ = 'Vincent'
from sqlalchemy import Column, Integer, String
from utils.bdd_base import Base, engine


class Track(Base):
    __tablename__ = 'Tracks'
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def from_json(self, json):
        self.id = json['id']
        self.name = json['name']

    def __repr__(self):
        return '{id: ' + str(self.id) + ', name: ' + str(self.name) + '}'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Base.metadata.create_all(engine)