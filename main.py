__author__ = 'Vincent'

from datetime import datetime

from gps import *
from beans.session import Session
from beans.gps_datas import GPSData
from utils.bdd import engine, db_session
import utils.config as config
import RPi.GPIO as GPIO
import time

# stop = False
#
#
# def press_button_callback(channel):
#     print("Stop session" + str(channel))
#     global stop
#     stop = True
#     print("Remove button event")
#     GPIO.remove_event_detect(config.PIN_NUMBER_BUTTON)


def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PIN_NUMBER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config.PIN_NUMBER_LED, GPIO.OUT)
    GPIO.setup(config.PIN_NUMBER_RUNING, GPIO.OUT)

    GPIO.output(config.PIN_NUMBER_RUNING, False)
    GPIO.output(config.PIN_NUMBER_LED, False)

def main():
    init()

    engine.connect()
    session = gps(mode=WATCH_ENABLE)
    GPIO.output(config.PIN_NUMBER_RUNING, True)

    try:
        while True:
            stop = False

            print("Push button to start")
            time.sleep(0.01)
            GPIO.wait_for_edge(config.PIN_NUMBER_BUTTON, GPIO.BOTH)

            # create new session and insert it
            track_session = Session(name="Session 1", start_date_time=datetime.utcnow())
            print("Insert: " + str(track_session))
            db_session.add(track_session)
            db_session.commit()

            # time.sleep(0.1)
            GPIO.add_event_detect(config.PIN_NUMBER_BUTTON, GPIO.BOTH)

            GPIO.output(config.PIN_NUMBER_LED, True)
            while not stop:
                # get the gps datas
                datas = session.next()

                if datas['class'] == "TPV":
                    # create gps datas and insert it
                    gps_data = GPSData(latitude=session.fix.latitude, longitude=session.fix.longitude,
                                       speed=session.fix.speed, date_time=session.fix.time, session=track_session)
                    print("Insert: " + str(gps_data))
                    db_session.add(gps_data)
                    db_session.commit()
                else:
                    print("No signal ...")

                if GPIO.event_detected(config.PIN_NUMBER_BUTTON):
                    stop = True

            GPIO.remove_event_detect(config.PIN_NUMBER_BUTTON)
            GPIO.output(config.PIN_NUMBER_LED, False)
            # GPIO.remove_event_detect(config.PIN_NUMBER_BUTTON)
            # update the session with end date time
            track_session.end_date_time = datetime.utcnow()
            print("Update: " + str(track_session))
            db_session.commit()

    except KeyError:
        print("Stop by the user")
    except StopIteration:
        print("GPSD is stopped")
    finally:
        session = None
        GPIO.output(config.PIN_NUMBER_RUNING, True)
        GPIO.cleanup()


if __name__ == "__main__":
    main()