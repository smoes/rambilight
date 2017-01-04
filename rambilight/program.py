import os
import time
import logging

from rambilight.calibration import edge_calibration
from rambilight.calibration import color_calibration
from rambilight.core import RambilightDriver
from imutils.video.pivideostream import PiVideoStream
from lib import ws2801
import imutils

rambilight_instance = None
stream = None

def stop_program():

    global rambilight_instance
    global stream


    if rambilight_instance is not None:
        rambilight_instance.stop()
        rambilight_instance = None
    time.sleep(0.5)
    stream.stop()
    ws2801.turn_off()
    ws2801.turn_off()


def run_program():

    global rambilight_instance
    global stream

    stream = PiVideoStream(resolution=(640, 480), framerate = 30).start()
    time.sleep(2)

    edge_config = "rambilight/config/edges.pickle"
    color_config = "rambilight/config/colors.pickle"

    edges = []
    if os.path.exists(edge_config):
        logging.info("Loading existing edge configuration")
        edges = edge_calibration.load_edge_calibration(edge_config)
    else:
        logging.error("No existing edge configuration found")
        logging.info("Rambilight could not be started.")
        return None 

    tv_res = (1920, 1080)
    led_width = 28
    led_height = 15


    if os.path.exists(color_config):
        logging.info("Loading existing color configuration")
        color_calibration.load_calibration(color_config, stream)
    else:
        logging.info("No existing color calibration found!")
        logging.info("Falling back to standard calibration.")
        color_calibration.decent_constant_calibration(stream.camera)

    rambilight = RambilightDriver(1, edges, stream)
    rambilight.start()
    rambilight_instance = rambilight
    return True

def keybindings():
    return {}

def name():
    return "rambilight"
