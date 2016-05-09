__author__ = 'Vincent'
import RPi.GPIO as GPIO
import threading
import time


class Led:
    def __init__(self, pin):
        self._GPIOPORT = pin
        self.stop_program = False

    def stop(self):
        self.stop_program = True

    def turn_on(self):
        GPIO.output(self._GPIOPORT, True)

    def turn_off(self):
        GPIO.output(self._GPIOPORT, False)

    def blink_error(self, e):
        delay_on = 0.3
        delay_off = 0.1
        self.__common_blink__(delay_on, delay_off, e)

    def blink(self, e):
        delay = 0.5
        self.__common_blink__(delay, delay, e)

    def blink_database_treatment(self, e):
        delay = 0.1
        self.__common_blink__(delay, delay, e)

    def __common_blink__(self, delay_on, delay_off, e):
        t1 = threading.Thread(target=self.blink_thread, args=(delay_on, delay_off, e))
        t1.start()

    def blink_thread(self, delaytime_on, delaytime_off, event):
        while not event.is_set():
            GPIO.output(self._GPIOPORT, False)
            time.sleep(delaytime_off)
            GPIO.output(self._GPIOPORT, True)
            time.sleep(delaytime_on)

        if not self.stop_program:
            event.wait()