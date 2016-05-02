__author__ = 'Vincent'

from threading import Thread
from threading import Event
import smbus
import math
from utils.bdd import *
from utils.functions import *

# Power management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c


def read_byte(adr):
    return bus.read_byte_data(address, adr)


def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr + 1)
    val = (high << 8) + low
    return val


def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
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


bus = smbus.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68  # This is the address value read via the i2cdetect command


class AccelerometerThread(Thread):
    def __init__(self, db_session):
        Thread.__init__(self)
        bus.write_byte_data(address, power_mgmt_1, 0)
        self.db_session = db_session
        self.can_run = Event()
        self.stop_program = Event()

    def run(self):
        while not self.stop_program.isSet():
            self.can_run.wait()

            while not self.stop_program.isSet() and self.can_run.isSet():
                gyro_x = (read_word_2c(0x43) / 131)
                gyro_y = (read_word_2c(0x45) / 131)
                gyro_z = (read_word_2c(0x47) / 131)
                accel_x = (read_word_2c(0x3b) / 16384.0)
                accel_y = (read_word_2c(0x3d) / 16384.0)
                accel_z = (read_word_2c(0x3f) / 16384.0)
                rot_x = get_x_rotation(accel_x, accel_y, accel_z)
                rot_y = get_y_rotation(accel_x, accel_y, accel_z)
                accelerometer_data = AccelerometerData(gyroscope_x=gyro_x, gyroscope_y=gyro_y, gyroscope_z=gyro_z,
                                                       accelerometer_x=accel_x, accelerometer_y=accel_y,
                                                       accelerometer_z=accel_z, rotation_x=rot_x, rotation_y=rot_y)
                log.log("Insert: " + str(accelerometer_data), log.LEVEL_DEBUG)
                self.db_session.add(accelerometer_data)
                self.db_session.commit()

        log.log("AccelerometerThread will be stopped !!", log.LEVEL_DEBUG)

    def pause(self):
        log.log("AccelerometerThread pausing ....", log.LEVEL_DEBUG)
        self.can_run.clear()

    def resume(self):
        log.log("AccelerometerThread resuming ....", log.LEVEL_DEBUG)
        self.can_run.set()

    def stop(self):
        log.log("AccelerometerThread stopping ....", log.LEVEL_DEBUG)
        self.stop_program.set()
        self.resume()
