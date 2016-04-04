__author__ = 'Vincent'

from datetime import datetime

from gps import *
from beans.session import Session
from beans.gps_datas import GPSData
from utils.bdd import *
import utils.config as config
import RPi.GPIO as GPIO
from datetime import date

# stop = False
#
#
# def press_button_callback(channel):
#     print("Stop session" + str(channel))
#     global stop
#     stop = True
#     print("Remove button event")
#     GPIO.remove_event_detect(config.PIN_NUMBER_BUTTON)


def start_track_session(track_id):
    track_session = Session()

    qry = db_session.query(func.max(Session.id_day_session).label("max_id_day_session")).filter(Session.date_session == date.today()).filter(Session.track_id == track_id)
    res = qry.one()

    id_day_session = 1
    if res.max_id_day_session is not None:
        id_day_session = res.max_id_day_session + 1

    track_session.date_session = date.today()
    track_session.track_id = track_id
    track_session.name = "Session " + str(id_day_session)
    track_session.id_day_session = id_day_session

    return track_session


def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PIN_NUMBER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config.PIN_NUMBER_LED, GPIO.OUT)
    GPIO.setup(config.PIN_NUMBER_RUNING, GPIO.OUT)

    GPIO.output(config.PIN_NUMBER_RUNING, False)
    GPIO.output(config.PIN_NUMBER_LED, False)


def main():
    init_gpio()

    engine.connect()
    session = gps(mode=WATCH_ENABLE)
    GPIO.output(config.PIN_NUMBER_RUNING, True)

    try:
        while True:
            stop = False

            print("Push button to start")
            GPIO.wait_for_edge(config.PIN_NUMBER_BUTTON, GPIO.FALLING)

            # create new session and insert it
            track_session = start_track_session(1)
            print("Insert: " + str(track_session))
            db_session.add(track_session)
            db_session.commit()

            GPIO.add_event_detect(config.PIN_NUMBER_BUTTON, GPIO.FALLING)
            GPIO.output(config.PIN_NUMBER_LED, True)

            while not stop:
                # get the gps datas
                if session.waiting():
                    datas = session.next()

                if datas['class'] == "TPV":
                    # create gps datas and insert it
                    gps_data = GPSData(latitude=session.fix.latitude, longitude=session.fix.longitude,
                                       speed=session.fix.speed, date_time=session.fix.time, session=track_session)
                    print("Insert: " + str(gps_data))
                    db_session.add(gps_data)
                    db_session.commit()

                if GPIO.event_detected(config.PIN_NUMBER_BUTTON):
                    print("Event detected stop recording !!!")
                    stop = True

            GPIO.remove_event_detect(config.PIN_NUMBER_BUTTON)
            GPIO.output(config.PIN_NUMBER_LED, False)

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