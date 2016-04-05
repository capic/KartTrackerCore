__author__ = 'Vincent'

from gps import *
from beans.gps_datas import GPSData
from utils.bdd import *
import utils.config as config
import RPi.GPIO as GPIO
from utils.functions import *


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

            end_track_session(track_session)
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