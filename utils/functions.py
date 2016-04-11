__author__ = 'Vincent'
import netifaces
import RPi.GPIO as GPIO
import time
import utils.config as config


def is_interface_up(interface):
    addr = netifaces.ifaddresses(interface)
    return netifaces.AF_INET in addr


def flash_led(stop):
    while not stop.isSet():
        GPIO.output(config.PIN_NUMBER_LED, False)
        time.sleep(0.5)
        GPIO.output(config.PIN_NUMBER_LED, True)
        time.sleep(0.5)


def led_on():
    GPIO.output(config.PIN_NUMBER_LED, True)
