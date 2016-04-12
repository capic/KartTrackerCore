__author__ = 'Vincent'
import utils.config as config
import RPi.GPIO as GPIO
import threading
import time


class Led:
    flagstop = 0
    flag = threading.Event()

    def __init__(self):
        self._GPIOPORT = config.PIN_NUMBER_LED
        GPIO.setwarnings(False)
        GPIO.setup(self._GPIOPORT, GPIO.OUT)
        self.flag.set()

    def turn_on(self):
        self.flag.clear()
        print 'Turn On ...'
        GPIO.output(self._GPIOPORT, True)

    def turn_off(self):
        self.flag.clear()
        print 'Turn Off ...'
        GPIO.output(self._GPIOPORT, False)

    def blink(self, delay, e):
        print 'Thread Blink Create ...'
        t1 = threading.Thread(target=self.blink_thread, args=(delay, e))
        t1.start()
        print 'Thread Started'

    def blink_thread(self, delaytime, event):
        print 'blink_thread Start ....'
        while not event:
            GPIO.output(self._GPIOPORT, False)
            time.sleep(delaytime)
            GPIO.output(self._GPIOPORT, True)
            time.sleep(delaytime)