__author__ = 'Vincent'

import getopt
from gps import *
from utils.bdd import *
from utils.functions import *
import os
from utils.led2 import Led
from time import sleep
from threading import Event
import smbus
import math


POWER_MGMT_1 = 0x6b
POWER_MGMT_2 = 0x6c
ADDRESS = 0x68  # This is the address value read via the i2cdetect command
bus = smbus.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
bus.write_byte_data(ADDRESS, POWER_MGMT_1, 0)


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
                config_object['log_output'] == "True" or config_object['log_output'] == "true" or config_object[
                    'log_output'] == "1")
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


def read_byte(adr):
    return bus.read_byte_data(ADDRESS, adr)


def read_word(adr):
    high = bus.read_byte_data(ADDRESS, adr)
    low = bus.read_byte_data(ADDRESS, adr + 1)
    val = (high << 8) + low
    return val


def read_word_2c(adr):
    val = read_word(adr)
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val


def dist(a, b):
    return math.sqrt((a * a) + (b * b))


def get_y_rotation(x, y, z):
    radians = math.atan2(x, dist(y, z))
    return -math.degrees(radians)


def get_x_rotation(x, y, z):
    radians = math.atan2(y, dist(x, z))
    return math.degrees(radians)


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
            led_thread.set_type_blink()

            track_id = args[0]
            track = db_session.query(Track).filter(Track.id == track_id).one()

            session = gps(mode=WATCH_ENABLE)

            # il faut pouvoir arreter le programme depuis l'interface
            while not stop_program:
                stop_recording = False
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
                        # GPIO.wait_for_edge(config.PIN_NUMBER_BUTTON, GPIO.FALLING)

                        while not stop_recording:
                            # get the gps datas
                            if session.waiting():
                                datas = session.next()

                            if datas['class'] == "TPV":
                                date_time = func.strftime('%Y-%m-%d %H:%M:%f', datetime.now())
                                # create gps datas and insert it
                                gps_data = GPSData(latitude=session.fix.latitude, longitude=session.fix.longitude,
                                                   speed=session.fix.speed,
                                                   date_time=date_time,
                                                   session_id=track_session.id)
                                log.log("Insert: " + str(gps_data), log.LEVEL_DEBUG)
                                db_session.add(gps_data)
                                # db_session.commit()

                                gyro_x = (read_word_2c(0x43) / 131)
                                gyro_y = (read_word_2c(0x45) / 131)
                                gyro_z = (read_word_2c(0x47) / 131)
                                accel_x = (read_word_2c(0x3b) / 16384.0)
                                accel_y = (read_word_2c(0x3d) / 16384.0)
                                accel_z = (read_word_2c(0x3f) / 16384.0)
                                rot_x = get_x_rotation(accel_x, accel_y, accel_z)
                                rot_y = get_y_rotation(accel_x, accel_y, accel_z)
                                accelerometer_data = AccelerometerData(gyroscope_x=gyro_x, gyroscope_y=gyro_y,
                                                                       gyroscope_z=gyro_z,
                                                                       accelerometer_x=accel_x, accelerometer_y=accel_y,
                                                                       accelerometer_z=accel_z, rotation_x=rot_x,
                                                                       rotation_y=rot_y,
                                                                       date_time=date_time,
                                                                       session_id=track_session.id)
                                log.log("Insert: " + str(accelerometer_data), log.LEVEL_DEBUG)
                                db_session.add(accelerometer_data)
                                db_session.commit()

                            if GPIO.event_detected(config.PIN_NUMBER_BUTTON):
                                stop_recording = True

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
            clean_end_program(led_thread)
    else:
        clean_end_program(led_thread)


if __name__ == "__main__":
    print("sys.argv =========> %s" % sys.argv)
    main(sys.argv[1:])
