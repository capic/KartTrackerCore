__author__ = 'Vincent'

import getopt
from gps import *
from beans.gps_datas import GPSData
from utils.bdd import *
import utils.log as log
from utils.functions import *
import os
import threading



def init_gpio():
    log.log("init_gpio", log.LEVEL_INFO)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PIN_NUMBER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config.PIN_NUMBER_LED, GPIO.OUT)
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


def program_waiting():
    led_on()


def program_running(start):
    flash_led(start)


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
    program_waiting()

    start_blinking = threading.Event()
    t = threading.Thread(name='non-block', target=program_running, args=(start_blinking, ))
    t.start()

    stop_program = False
    try:
        # il faut pouvoir arreter le programme depuis l'interface
        while not stop_program:
            stop_recording = False

            print("Push button to start")
            GPIO.wait_for_edge(config.PIN_NUMBER_BUTTON, GPIO.FALLING)
            start_blinking.set()

            # create new session and insert it
            track_session = start_track_session(track.id)

            GPIO.add_event_detect(config.PIN_NUMBER_BUTTON, GPIO.FALLING)

            while not stop_recording:
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
                    stop_recording = True

            GPIO.remove_event_detect(config.PIN_NUMBER_BUTTON)
            start_blinking.clear()

            program_waiting()

            end_track_session(track_session)
    except KeyError:
        log.log("Stop by the user", log.LEVEL_ERROR)
    except StopIteration:
        log.log("GPSD is stopped", log.LEVEL_ERROR)
    finally:
        log.log("Cleanup program", log.LEVEL_INFO)
        session = None
        GPIO.cleanup()


if __name__ == "__main__":
    main(sys.argv[1:])