import os
import time
import logging

from rambilight.calibration import edge_calibration
from rambilight.calibration import color_calibration
from rambilight.core import RambilightDriver
from imutils.video.pivideostream import PiVideoStream
from lib import ws2801
from lib import server
import imutils

rambilight_instance = None
stream = None

server_instance = None

tv_res = (1920, 1080)
led_width = 28
led_height = 15

edge_config = "rambilight/config/edges.pickle"
color_config = "rambilight/config/colors.pickle"

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

    ws2801.pulse()

    stream = PiVideoStream(resolution=(640, 480), framerate = 30).start()
    time.sleep(2)

    edges = load_edges()

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


def load_edges():
    if os.path.exists(edge_config):
        logging.info("Loading existing edge configuration")
        return edge_calibration.load_edge_calibration(edge_config)
    else:
        logging.info("No existing edge configuration found")
        return None


def keybindings():
    ri = rambilight_instance
    return {'KEY_STOP': calibrate_edges,
            'KEY_PLAY': calibrate_color,
            'KEY_LEFT': ri.dec_r_shift,
            'KEY_RIGHT': ri.inc_r_shift,
            'KEY_UP': ri.inc_b_shift,
            'KEY_DOWN': ri.dec_b_shift,
            'KEY_OK': ri.inc_g_shift,
            'KEY_INFO': ri.dec_g_shift,
            'KEY_MODE': ri.dec_brightness,
            'KEY_SUBTITLE': ri.inc_brightness
    }

def calibrate_edges():
    rambilight_instance.pause()
    ws2801.pulse()
    global server_instance

    if server_instance is None:
        server_instance = server.init_simple_http()

    edges = edge_calibration.find_edges(stream, tv_res, led_width, led_height)

    if edges:
        edge_calibration.backup_edges(edges, edge_config)
        rambilight_instance.unpause()

def calibrate_color():
    rambilight_instance.pause()
    ws2801.pulse()
    global server_instance

    if server_instance is None:
        server_instance = server.init_simple_http()

    edges = load_edges()
    calib = None
    if edges is not None:
        calib = color_calibration.calibrate(stream, edges, tv_res, led_width, led_height)

    if calib:
        color_calibration.backup_calibration(calib, color_config)
        rambilight_instance.unpause()



def name():
    return "rambilight"
