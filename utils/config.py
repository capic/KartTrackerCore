__author__ = 'Vincent'

BDD_TYPE = 'sqlite'
BDD_PATH = '/home/pi/KartTracker/'
BDD_NAME = 'karttracker.db'
BDD_STRING_CONNECTION = BDD_TYPE + ':///' + BDD_PATH + BDD_NAME

PIN_NUMBER_BUTTON = 13
PIN_NUMBER_LED = 26

REST_ADDRESS = "http://192.168.1.101:4000/"

CONFIG_LOG_LEVEL = 0
CONFIG_LOG_LEVEL_LOGGING = 0

CONFIG_FILE = '/home/pi/KartTracker/conf/conf.cfg'

LOG_OUTPUT = True
CONSOLE_OUTPUT = True
LOG_BDD = False

DEFAULT_UNIREST_TIMEOUT = 30
FAST_UNIREST_TIMEOUT = 3

RECORDING_INTERVAL = 0