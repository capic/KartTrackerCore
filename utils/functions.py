__author__ = 'Vincent'
import netifaces
import RPi.GPIO as GPIO
import time
import utils.config as config


def is_interface_up(interface):
    addr = netifaces.ifaddresses(interface)
    return netifaces.AF_INET in addr


def flash_led(stop_blinking):
    while not stop_blinking.isSet():
        print('led off')
        GPIO.output(config.PIN_NUMBER_LED, False)
        time.sleep(0.5)
        print('led on')
        GPIO.output(config.PIN_NUMBER_LED, True)
        time.sleep(0.5)

    stop_blinking.wait()


def led_on():
    GPIO.output(config.PIN_NUMBER_LED, True)
