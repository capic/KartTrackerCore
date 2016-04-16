__author__ = 'Vincent'

import getopt
from gps import *
from utils.bdd import *
from utils.functions import *
import os
import threading
from utils.led import Led


def init_gpio():
    log.log("init_gpio", log.LEVEL_INFO)

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(config.PIN_NUMBER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)


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
        if 'pin_number_button' in config_object:
            config.PIN_NUMBER_BUTTON = config_object['pin_number_button']
        if 'pin_number_led' in config_object:
            config.PIN_NUMBER_BUTTON = config_object['pin_number_led']

        log.log("Rest Address: %s" % config.REST_ADDRESS, log.LEVEL_DEBUG)
        log.log("Log output %s" % str(config.LOG_OUTPUT), log.LEVEL_DEBUG)
        log.log("Console output %s" % str(config.CONSOLE_OUTPUT), log.LEVEL_DEBUG)
    else:
        print("config file not found")


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "uds", ["upload", "download", "synchronize"])
    except getopt.GetoptError:
        exit()

    init_config()
    to_upload = False
    to_download = False

    for o, a in opts:
        if o in ("-u", "--upload"):
            log.log("Upload mode", log.LEVEL_DEBUG)
            to_upload = True
        elif o in ("-d", "--download"):
            log.log("Download mode", log.LEVEL_DEBUG)
            to_download = True
        elif o in ("-s", "--synchronize"):
            log.log("synchronize mode", log.LEVEL_DEBUG)
            to_upload = True
            to_download = True
        else:
            assert False, "unhandled option"

    if to_upload:
        send_to_central_database()

    if to_download:
        update_from_central_database()

    init_gpio()

    log.log("Starting ....", log.LEVEL_INFO)

    if len(args) != 1:
        log.log("No track id chosen", log.LEVEL_ERROR)
        exit()

    engine.connect()
    session = gps(mode=WATCH_ENABLE)

    led = Led()
    led.turn_on()

    e = threading.Event()

    stop_program = False
    try:
        track_id = args[0]
        track = db_session.query(Track).filter(Track.id == track_id).one()

        # il faut pouvoir arreter le programme depuis l'interface
        while not stop_program:
            stop_recording = False

            print("Push button to start")
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(config.PIN_NUMBER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.wait_for_edge(config.PIN_NUMBER_BUTTON, GPIO.FALLING)
            e.set()
            e.clear()
            led.blink(e)

            try:
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
                                           speed=session.fix.speed, date_time=session.fix.time, session_id=track_session.id)
                        log.log("Insert: " + str(gps_data), log.LEVEL_DEBUG)
                        db_session.add(gps_data)
                        db_session.commit()
                    else:
                        log.log("No gps datas", log.LEVEL_DEBUG)

                    if GPIO.event_detected(config.PIN_NUMBER_BUTTON):
                        log.log("Event detected stop recording !!!", log.LEVEL_DEBUG)
                        stop_recording = True

                GPIO.remove_event_detect(config.PIN_NUMBER_BUTTON)
                log.log("Stop blinking ...", log.LEVEL_DEBUG)
                e.set()
                led.turn_on()
                time.sleep(1)

                end_track_session(track_session)
            except Exception:
                led.blink_error(e)
                raise
    except KeyError:
        log.log("Stop by the user", log.LEVEL_ERROR)
    except StopIteration:
        log.log("GPSD is stopped", log.LEVEL_ERROR)
    finally:
        session = None
        e.set()
        led.turn_off()

    log.log("Cleanup program", log.LEVEL_INFO)
    GPIO.cleanup()


if __name__ == "__main__":
    main(sys.argv[1:])