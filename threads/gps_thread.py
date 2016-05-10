__author__ = 'Vincent'

from threading import Thread
from threading import Event
from gps import *
from utils.bdd import *
from utils.functions import *


class GpsThread(Thread):
    def __init__(self, session_db):
        Thread.__init__(self)
        self.session = gps(mode=WATCH_ENABLE)
        self.db_session = session_db
        self.recording_interval = 0
        self.track_session_id = 0
        self.can_run = Event()
        self.stop_program = Event()

    def set_recording_inteval(self, recording_interval):
        self.recording_interval = recording_interval

    def set_track_session_id(self, track_session_id):
        self.track_session_id = track_session_id

    def run(self):
        while not self.stop_program.isSet():
            self.can_run.wait()

            while not self.stop_program.isSet() and self.can_run.isSet():
                # get the gps datas
                # if self.session.waiting():
                datas = self.session.next()

                if datas['class'] == "TPV":
                    # create gps datas and insert it
                    gps_data = GPSData(latitude=self.session.fix.latitude, longitude=self.session.fix.longitude,
                                       speed=self.session.fix.speed, date_time=self.session.fix.time,
                                       session_id=self.track_session_id)
                    log.log("Insert: " + str(gps_data), log.LEVEL_DEBUG)
                    self.db_session.add(gps_data)
                    self.db_session.commit()
                else:
                    log.log("No gps datas", log.LEVEL_DEBUG)

                time.sleep(self.recording_interval)
        log.log("GpsThread will be stopped !!", log.LEVEL_DEBUG)
        self.session = None

    def pause(self):
        log.log("GpsThread pausing ....", log.LEVEL_DEBUG)
        self.can_run.clear()

    def resume(self):
        log.log("GpsThread resuming ....", log.LEVEL_DEBUG)
        self.can_run.set()

    def stop(self):
        log.log("GpsThread stopping ....", log.LEVEL_DEBUG)
        self.stop_program.set()
        self.resume()
