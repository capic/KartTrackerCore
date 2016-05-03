__author__ = 'Vincent'

from threading import Thread
from threading import Event
import smbus
import math
from utils.bdd import *
from utils.functions import *


class AccelerometerThread(Thread):
    # Power management registers
    POWER_MGMT_1 = 0x6b
    POWER_MGMT_2 = 0x6c
    ADDRESS = 0x68  # This is the address value read via the i2cdetect command
    
    def __init__(self, db_session):
        Thread.__init__(self)
        self.db_session = db_session
        self.can_run = Event()
        self.stop_program = Event()
        try:
            self.bus = smbus.SMBus(0)  # or bus = smbus.SMBus(1) for Revision 2 boards
            self.bus.write_byte_data(self.ADRRESS, self.POWER_MGMT_1, 0)
        except Exception:
            log.log("Error smbus", log.LEVEL_DEBUG)
            self.stop()
            
    def run(self):
        log.log("I set ? %s" % self.stop_program.isSet(), log.LEVEL_DEBUG)
        while not self.stop_program.isSet():
            self.can_run.wait()

            while not self.stop_program.isSet() and self.can_run.isSet():
                gyro_x = (self.read_word_2c(0x43) / 131)
                gyro_y = (self.read_word_2c(0x45) / 131)
                gyro_z = (self.read_word_2c(0x47) / 131)
                accel_x = (self.read_word_2c(0x3b) / 16384.0)
                accel_y = (self.read_word_2c(0x3d) / 16384.0)
                accel_z = (self.read_word_2c(0x3f) / 16384.0)
                rot_x = self.get_x_rotation(accel_x, accel_y, accel_z)
                rot_y = self.get_y_rotation(accel_x, accel_y, accel_z)
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
        
    def read_byte(self, adr):
        return self.bus.read_byte_data(self.ADDRESS, adr)

    def read_word(self, adr):
        high = self.bus.read_byte_data(self.ADDRESS, adr)
        low = self.bus.read_byte_data(self.ADDRESS, adr + 1)
        val = (high << 8) + low
        return val
    
    def read_word_2c(self, adr):
        val = self.read_word(adr)
        if val >= 0x8000:
            return -((65535 - val) + 1)
        else:
            return val
    
    def dist(self, a, b):
        return math.sqrt((a * a) + (b * b))
    
    def get_y_rotation(self, x, y, z):
        radians = math.atan2(x, self.dist(y, z))
        return -math.degrees(radians)
    
    def get_x_rotation(self, x, y, z):
        radians = math.atan2(y, self.dist(x, z))
        return math.degrees(radians)
