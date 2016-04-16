__author__ = 'Vincent'
import RPi.GPIO as GPIO
import threading
import time


class Led:
    def __init__(self, pin):
        self._GPIOPORT = pin
        GPIO.setwarnings(False)
        GPIO.setup(self._GPIOPORT, GPIO.OUT)

    def turn_on(self):
        GPIO.output(self._GPIOPORT, True)

    def turn_off(self):
        GPIO.output(self._GPIOPORT, False)

    def blink_error(self, e):
        delay = 0.1
        t1 = threading.Thread(target=self.blink_thread, args=(delay, e))
        t1.start()

    def blink(self, e):
        delay = 0.5
        t1 = threading.Thread(target=self.blink_thread, args=(delay, e))
        t1.start()

    def blink_thread(self, delaytime, event):
        while not event.is_set():
            GPIO.output(self._GPIOPORT, False)
            time.sleep(delaytime)
            GPIO.output(self._GPIOPORT, True)
            time.sleep(delaytime)

        event.wait()