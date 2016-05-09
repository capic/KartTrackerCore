__author__ = 'Vincent'
import RPi.GPIO as GPIO
from threading import Thread
from threading import Event
import time


class Led(Thread):
    def __init__(self, pin):
        Thread.__init__(self)
        self._GPIOPORT = pin
        self.blinking = Event()
        self.stop_program = Event()
        self.delay_on = 0
        self.delay_off = 0

    def run(self):
        while not self.stop_program.isSet():
            self.blinking.wait()

            while self.blinking.is_set():
                GPIO.output(self._GPIOPORT, False)
                time.sleep(self.delay_off)
                GPIO.output(self._GPIOPORT, True)
                time.sleep(self.delay_on)

    def resume(self):
        self.blinking.set()

    def pause(self):
        self.blinking.clear()

    def stop(self):
        self.stop_program.set()

    def turn_on(self):
        GPIO.output(self._GPIOPORT, True)

    def turn_off(self):
        GPIO.output(self._GPIOPORT, False)

    def set_type_blink_error(self):
        self.delay_on = 0.3
        self.delay_off = 0.1

    def set_type_blink(self):
        self.delay_on = self.delay_off = 0.5

    def set_type_blink_database_treatment(self):
        self.delay_on = self.delay_off = 0.1