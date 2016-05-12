__author__ = 'Vincent'

from threading import Thread
from threading import Event
from gps import *
from utils.bdd import *
from utils.functions import *


class GpsThread(Thread):
    def __init__(self, session_db, event):
        Thread.__init__(self)
        self.db_session = session_db
        self.recording_interval = 0
        self.track_session_id = 0
        self.can_run = Event()
        self.stop_program = Event()
        self.event = event

    def set_recording_inteval(self, recording_interval):
        self.recording_interval = recording_interval

    def set_track_session_id(self, track_session_id):
        self.track_session_id = track_session_id

    def run(self):
        session = gps(mode=WATCH_ENABLE)

        while not self.stop_program.isSet():
            self.can_run.wait()

            while not self.stop_program.isSet() and self.can_run.isSet():
                # get the gps datas
                if session.waiting():
                    datas = session.next()

                if datas['class'] == "TPV":
                    self.event.set()
                    # create gps datas and insert it
                    gps_data = GPSData(latitude=session.fix.latitude, longitude=session.fix.longitude,
                                       speed=session.fix.speed,
                                       # date_time=datetime.now().strftime('%Y-%m-%d %H:%M:%f'),
                                       session_id=self.track_session_id)
                    log.log("Insert: " + str(gps_data), log.LEVEL_DEBUG)
                    self.db_session.add(gps_data)
                    self.db_session.commit()
                    self.event.clear()

                time.sleep(self.recording_interval)

        log.log("GpsThread stopped !!", log.LEVEL_DEBUG)
        session = None

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
