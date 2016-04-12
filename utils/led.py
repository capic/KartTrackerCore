__author__ = 'Vincent'
import utils.config as config
import RPi.GPIO as GPIO
import threading
import time


class Led:
    # flag = threading.Event()

    def __init__(self):
        self._GPIOPORT = config.PIN_NUMBER_LED
        GPIO.setwarnings(False)
        GPIO.setup(self._GPIOPORT, GPIO.OUT)

    def turn_on(self):
        GPIO.output(self._GPIOPORT, True)

    def turn_off(self):
        # self.flag.clear()
        GPIO.output(self._GPIOPORT, False)

    def blink(self, delay, e):
        t1 = threading.Thread(target=self.blink_thread, args=(delay, e))
        t1.start()

    def blink_thread(self, delaytime, event):
        while not event.is_set():
            GPIO.output(self._GPIOPORT, False)
            time.sleep(delaytime)
            GPIO.output(self._GPIOPORT, True)
            time.sleep(delaytime)

        event.wait()