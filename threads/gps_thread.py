__author__ = 'Vincent'

from threading import Thread
from threading import Event
from gps import *
from utils.bdd import *
from utils.functions import *


class GpsThread(Thread):
    def __init__(self, db_session):
        Thread.__init__(self)
        self.session = gps(mode=WATCH_ENABLE)
        self.db_session = db_session
        self.can_run = Event()
        self.stop_program = Event()

    def run(self):
        while not self.stop_program.isSet():
            self.can_run.wait()
            
            while not self.stop_program.isSet() and self.can_run.isSet():
                # get the gps datas
                if self.session.waiting():
                    datas = self.session.next()
    
                if datas['class'] == "TPV":
                    # create gps datas and insert it
                    gps_data = GPSData(latitude=session.fix.latitude, longitude=session.fix.longitude,
                                       speed=session.fix.speed, date_time=session.fix.time, session_id=track_session.id)
                    log.log("Insert: " + str(gps_data), log.LEVEL_DEBUG)
                    self.db_session.add(gps_data)
                    self.db_session.commit()
                else:
                    log.log("No gps datas", log.LEVEL_DEBUG)
        log.log("GpsThread will be stopped !!")

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
