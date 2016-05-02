__author__ = 'Vincent'
from sqlalchemy import *
from sqlalchemy.orm import (scoped_session, sessionmaker, relationship, backref)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Time, Boolean
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
    new = Column(Boolean)
    session = relationship("Session")

    def __repr__(self):
        return '{id: ' + str(self.id) + ', name: ' + str(self.name) + '}'

    def from_json(self, json):
        self.id = json['id']
        self.name = json['name']


# ############ SESSION ############


class Session(Base):
    __tablename__ = 'session'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    id_day_session = Column(Integer)
    date_session = Column(Date)
    name = Column(String)
    start_time = Column(Time)
    end_time = Column(Time)

    gps_datas = relationship("GPSData", cascade="delete")
    accelerometer_datas = relationship("AccelerometerData", cascade="delete")
    track_id = Column(Integer, ForeignKey('track.id'))

    def __repr__(self):
        return '<Session>:{id: ' + str(self.id) + ', id_day_session: ' + str(
            self.id_day_session) + ', date_session: ' + str(
            self.date_session) + ', name: ' + str(self.name) + ', start_time: ' + str(
            self.start_time) + ', end_time: ' + str(self.end_time) + ', track_id: ' + str(
            self.track_id) + '}'

    def _from_json(self, json):
        self.id = json['id']
        self.id_day_session = json['id_day_session']
        self.date_session = json['date_session']
        self.name = json['name']
        self.start_time = json['start_time']
        self.end_time = json['end_time']

        for gps_data_json in json['gps_datas']:
            gps_data = GPSData()
            gps_data._from_json(gps_data_json)
            self.gps_datas.append(gps_data)

        for accelerometer_data_json in json['accelerometer_datas']:
            accelerometer_data = AccelerometerData()
            accelerometer_data._from_json(accelerometer_data)
            self.accelerometer_datas.append(accelerometer_data)


# ############### GPS DATA ##############


class GPSData(Base):
    __tablename__ = 'gps_data'
    __table_args__ = {'sqlite_autoincrement': True}
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

    def _from_json(self, json):
        self.id = json['id']
        self.latitude = json['latitude']
        self.longitude = json['longitude']
        self.speed = json['speed']
        self.date_time = json['date_time']


# ############ ACCELEROMETER DATA ################


class AccelerometerData(Base):
    __tablename__ = "accelerometer_data"
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column(Integer, primary_key=True)
    gyroscope_x = Column(Float)
    gyroscope_y = Column(Float)
    gyroscope_z = Column(Float)
    accelerometer_x = Column(Float)
    accelerometer_y = Column(Float)
    accelerometer_z = Column(Float)
    rotation_x = Column(Float)
    rotation_y = Column(Float)

    session_id = Column(Integer, ForeignKey('session.id'))

    def __repr__(self):
        return '{id: ' + str(self.id) + ', gyroscope_x: ' + str(self.gyroscope_x) + ', gyroscope_y: ' + str(
            self.gyroscope_y) + ', gyroscope_z: ' + str(self.gyroscope_z) + ', accelerometer_x: ' + str(
            self.accelerometer_x) + ', accelerometer_y: ' + str(self.accelerometer_y) + ', accelerometer_z: ' + str(
            self.accelerometer_z) + ', rotation_x: ' + str(self.rotation_x) + ', rotation_y: ' + str(
            self.rotation_y) + '}'

    def _from_json(self, json):
        self.id = json['id']
        self.gyroscope_x = json['gyroscope_x']
        self.gyroscope_y = json['gyroscope_y']
        self.gyroscope_z = json['gyroscope_z']
        self.accelerometer_x = json['accelerometer_x']
        self.accelerometer_y = json['accelerometer_y']
        self.accelerometer_z = json['accelerometer_z']
        self.rotation_x = json['rotation_x']
        self.rotation_y = json['rotation_y']


# Base.query = db_session.query_property()
Base.metadata.create_all(engine)