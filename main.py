__author__ = 'Vincent'

import getopt
from gps import *
from utils.bdd import *
from utils.functions import *
import os
from utils.led2 import Led
from time import sleep
from threads.gps_thread import GpsThread
from threads.accelerometer_thread import AccelerometerThread

gps_thread = GpsThread(db_session)
accelerometer_thread = AccelerometerThread(db_session)


def init_gpio():
    log.log("init_gpio", log.LEVEL_INFO)

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(config.PIN_NUMBER_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(config.PIN_NUMBER_LED, GPIO.OUT)


def init_config():
    print("init_config with file %s " % config.CONFIG_FILE)

    if os.path.isfile(config.CONFIG_FILE):
        print("config file found")
        config_object = {}
        execfile(config.CONFIG_FILE, config_object)

        if 'bdd_path' in config_object:
            config.BDD_PATH = config_object['bdd_path']
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
            config.PIN_NUMBER_LED = config_object['pin_number_led']
        if 'recording_interval' in config_object:
            config.RECORDING_INTERVAL = config_object['recording_interval']

        log.log("Bdd path: %s" % config.BDD_PATH, log.LEVEL_DEBUG)
        log.log("Rest Address: %s" % config.REST_ADDRESS, log.LEVEL_DEBUG)
        log.log("Log output %s" % str(config.LOG_OUTPUT), log.LEVEL_DEBUG)
        log.log("Console output %s" % str(config.CONSOLE_OUTPUT), log.LEVEL_DEBUG)
        log.log("Log bdd %s" % str(config.LOG_BDD), log.LEVEL_DEBUG)
        log.log("Pin number button %d" % config.PIN_NUMBER_BUTTON, log.LEVEL_DEBUG)
        log.log("Pin number led %d" % config.PIN_NUMBER_LED, log.LEVEL_DEBUG)
    else:
        print("config file not found")


def clean_end_program(led_thread):
    led_thread.stop()
    led_thread.join()
    led_thread.turn_off()
    log.log("Cleanup program", log.LEVEL_INFO)
    GPIO.cleanup()

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "udsp:", ["upload", "download", "synchronize", "database-path"])
    except getopt.GetoptError:
        exit()

    init_config()
    init_gpio()

    to_upload = False
    to_download = False

    led_thread = Led(config.PIN_NUMBER_LED)
    led_thread.start()
    led_thread.turn_on()

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
        elif o in ("-p", "--database-path"):
            log.log("database path %s" % a, log.LEVEL_DEBUG)
            config.BDD_STRING_CONNECTION = config.BDD_TYPE + ':///' + a + config.BDD_NAME
            log.log("Connection string %s" % config.BDD_STRING_CONNECTION, log.LEVEL_DEBUG)
        else:
            assert False, "unhandled option"

    stop_program = False

    if to_upload:
        try:
            led_thread.set_type_blink_database_treatment()
            led_thread.resume()
            send_to_central_database()
        except:
            led_thread.set_type_blink_error()
            led_thread.resume()
            sleep(2)
            stop_program = True
        finally:
            led_thread.pause()

    if to_download:
        try:
            led_thread.set_type_blink_database_treatment()
            led_thread.resume()
            update_from_central_database()
        except:
            led_thread.set_type_blink_error()
            led_thread.resume()
            sleep(2)
            stop_program = True
        finally:
            led_thread.pause()

    led_thread.turn_on()

    log.log("Starting ....", log.LEVEL_INFO)

    engine.connect()

    if len(args) != 1:
        log.log("No track id chosen", log.LEVEL_ERROR)
        stop_program = True
    else:
        log.log("Track id: %s" % args[0], log.LEVEL_DEBUG)

    if not stop_program:
        try:
            gps_thread.start()
            gps_thread.pause()
            accelerometer_thread.start()
            accelerometer_thread.pause()
            led_thread.set_type_blink()

            track_id = args[0]
            track = db_session.query(Track).filter(Track.id == track_id).one()

            # il faut pouvoir arreter le programme depuis l'interface
            while not stop_program:
                print("Push button to start recording or long press to quit")
                GPIO.wait_for_edge(config.PIN_NUMBER_BUTTON, GPIO.FALLING)
                sleep(0.5)
                # after a short wait we test if the button is still pressed to avoid to wait a long time if we do a short pressed
                if GPIO.input(config.PIN_NUMBER_BUTTON) == GPIO.LOW:
                    sleep(2)
                    # if it's still pressed then we have to quit the program
                    if GPIO.input(config.PIN_NUMBER_BUTTON) == GPIO.LOW:
                        log.log("Button still pressed", log.LEVEL_DEBUG)
                        stop_program = True

                if not stop_program:
                    led_thread.resume()

                    try:
                        # create new session and insert it
                        track_session = start_track_session(track.id)
                        gps_thread.set_recording_inteval(config.RECORDING_INTERVAL)
                        accelerometer_thread.set_recording_inteval(config.RECORDING_INTERVAL)
                        gps_thread.set_track_session_id(track_session.id)
                        accelerometer_thread.set_track_session_id(track_session.id)

                        gps_thread.resume()
                        accelerometer_thread.resume()
                        GPIO.wait_for_edge(config.PIN_NUMBER_BUTTON, GPIO.FALLING)
                        gps_thread.pause()
                        accelerometer_thread.pause()

                        # GPIO.remove_event_detect(config.PIN_NUMBER_BUTTON)
                        log.log("Stop blinking ...", log.LEVEL_DEBUG)
                        led_thread.pause()
                        led_thread.turn_on()
                        time.sleep(.5)

                        end_track_session(track_session)
                    except Exception:
                        log.log("Exception in the program execution", log.LEVEL_ERROR)
                        led_thread.pause()
                        led_thread.set_type_blink_error()
                        led_thread.resume()
                        raise
        except KeyError:
            log.log("Stop by the user", log.LEVEL_ERROR)
        except StopIteration:
            log.log("GPSD is stopped", log.LEVEL_ERROR)
        finally:
            log.log("Finally execution ---", log.LEVEL_DEBUG)
            gps_thread.stop()
            accelerometer_thread.stop()
            gps_thread.join()
            accelerometer_thread.join()
            clean_end_program(led_thread)
    else:
        clean_end_program(led_thread)


if __name__ == "__main__":
    print("sys.argv =========> %s" % sys.argv)
    main(sys.argv[1:])
