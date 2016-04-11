__author__ = 'Vincent'
import netifaces
import RPi.GPIO as GPIO
import time


def is_interface_up(interface):
    addr = netifaces.ifaddresses(interface)
    return netifaces.AF_INET in addr


def flash_led(stop):
    while not stop:
        GPIO.output(config.PIN_NUMBER_LED, False)
        time.sleep(0.5)
        GPIO.output(config.PIN_NUMBER_LED, True)
        time.sleep(0.5)


def led_on():
    GPIO.output(config.PIN_NUMBER_LED, True)
