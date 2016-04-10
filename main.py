__author__ = 'Vincent'

import getopt
from gps import *
from beans.gps_datas import GPSData
from beans.track import Track
import utils.config as config
import RPi.GPIO as GPIO
from utils.bdd import *
import utils.log as log
import os


def init_gpio():
    log.log("init_gpio", log.LEVEL_INFO)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PIN_NUMBER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config.PIN_NUMBER_LED, GPIO.OUT)
    GPIO.setup(config.PIN_NUMBER_RUNING, GPIO.OUT)

    GPIO.output(config.PIN_NUMBER_RUNING, False)
    GPIO.output(config.PIN_NUMBER_LED, False)


def init_config():
    print("init_config with file %s " % config.CONFIG_FILE)

    if os.path.isfile(config.CONFIG_FILE):
        print("config file found")
        config_object = {}
        execfile(config.CONFIG_FILE, config_object)

        if 'rest_adresse' in config_object:
            config.REST_ADRESSE = config_object['rest_adresse']
        if 'log_output' in config_object:
            config.LOG_OUTPUT = (
                config_object['log_output'] == "True" or config_object['log_output'] == "true" or config_object['log_output'] == "1")
        if 'console_output' in config_object:
            config.CONSOLE_OUTPUT = (
                config_object['console_output'] == "True" or config_object['console_output'] == "true" or config_object[
                    'console_output'] == "1")
        if 'log_bdd' in config_object:
            config.LOG_BDD = (
                config_object['log_bdd'] == "True" or config_object['log_bdd'] == "true" or config_object[
                    'log_bdd'] == "1")
        if 'log_level' in config_object:
            config.CONFIG_LOG_LEVEL = config_object['log_level']
            log.convert_log_level_to_logging_level()

        log.log("Rest Address: %s" % config.REST_ADRESSE, log.LEVEL_DEBUG)
        log.log("Log output %s" % str(config.LOG_OUTPUT), log.LEVEL_DEBUG)
        log.log("Console output %s" % str(config.CONSOLE_OUTPUT), log.LEVEL_DEBUG)
    else:
        print("config file not found")

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "", [])
    except getopt.GetoptError:
        exit()

    init_config()

    log.log("Starting ....", log.LEVEL_INFO)
    # TODO: on ne doit envoyer seulement quand on veut importer en base centrale (avec un switch ? ou quand on recupere la connexion ?)
    send_to_central_database()

    update_from_central_database()

    if len(args) != 1:
        log.log("No track id chosen", log.LEVEL_ERROR)
        exit()

    track_id = args[0]
    track = db_session.query(Track).filter(Track.id == track_id).one()

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
            track_session = start_track_session(track.id)

            GPIO.add_event_detect(config.PIN_NUMBER_BUTTON, GPIO.FALLING)
            GPIO.output(config.PIN_NUMBER_LED, True)

            while not stop:
                # get the gps datas
                if session.waiting():
                    datas = session.next()

                if datas['class'] == "TPV":
                    # create gps datas and insert it
                    gps_data = GPSData(latitude=session.fix.latitude, longitude=session.fix.longitude,
                                       speed=session.fix.speed, date_time=session.fix.time, session_id=track_session.id,
                                       session=track_session)
                    log.log("Insert: " + str(gps_data), log.LEVEL_DEBUG)
                    db_session.add(gps_data)
                    db_session.commit()

                if GPIO.event_detected(config.PIN_NUMBER_BUTTON):
                    log.log("Event detected stop recording !!!", log.LEVEL_DEBUG)
                    stop = True

            GPIO.remove_event_detect(config.PIN_NUMBER_BUTTON)
            GPIO.output(config.PIN_NUMBER_LED, False)

            end_track_session(track_session)
    except KeyError:
        log.log("Stop by the user", log.LEVEL_ERROR)
    except StopIteration:
        log.log("GPSD is stopped", log.LEVEL_ERROR)
    finally:
        log.log("Cleanup program", log.LEVEL_INFO)
        session = None
        GPIO.output(config.PIN_NUMBER_RUNING, True)
        GPIO.cleanup()


if __name__ == "__main__":
    main(sys.argv[1:])