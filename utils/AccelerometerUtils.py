__author__ = 'Vincent'

import smbus
import math

POWER_MGMT_1 = 0x6b
POWER_MGMT_2 = 0x6c
ADDRESS = 0x68  # This is the address value read via the i2cdetect command
bus = smbus.SMBus(1)  # or bus = smbus.SMBus(1) for Revision 2 boards
bus.write_byte_data(ADDRESS, POWER_MGMT_1, 0)


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