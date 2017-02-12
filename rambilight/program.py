"""
Module to define the rambilight program.
Contains run_program, stop_program, key_binding and name
methods as a convention. For further details about programs
in this project, check out the readme. 
"""

import os
import time
import sys
import logging

from rambilight.calibration import edge_calibration
from rambilight.calibration import color_calibration
from rambilight.core import RambilightDriver
from imutils.video.pivideostream import PiVideoStream
from lib import ws2801
from lib import server
import imutils

sys.path.insert(1, "/usr/local/lib/python2.7/site-packages/")
import cv2


rambilight_instance = None
stream = None

server_instance = None

tv_res = (1920, 1080) # TV Resolution for calibration images
led_width = 28        # Number of horinzontal leds in rambilight
led_height = 15       # Number of vertical leds in rambilight

edge_file = "rambilight/config/edges.pickle"
color_file = "rambilight/config/colors.pickle"

def stop_program():
    """
    Stops the program, the imutils/picamera stream and
    turns of the leds.
    """

    global rambilight_instance
    global stream


    if rambilight_instance is not None:
        rambilight_instance.stop()
        rambilight_instance = None
    time.sleep(0.5)

    ws2801.pulse() # pulsing as feedback

    stream.stop()
    ws2801.turn_off()
    ws2801.turn_off()


def run_program():
    """
    Runs the program. It therefore creates a new picamera
    stream, loads existing configurations and starts the
    rambilight thread.
    """

    global rambilight_instance
    global stream

    ws2801.pulse()

    stream = PiVideoStream(resolution=(640, 480), framerate = 30).start()
    time.sleep(2)

    edges = load_edges()

    if os.path.exists(color_file):
        logging.info("Loading existing color configuration")
        color_calibration.load_calibration(color_file, stream)
    else:
        logging.info("No existing color calibration found!")
        logging.info("Falling back to standard calibration.")
        color_calibration.decent_constant_calibration(stream.camera)

    rambilight = RambilightDriver(1, edges, stream)
    rambilight.start()
    rambilight_instance = rambilight
    return True


def load_edges():
    """
    Loads edge configuration from file if exists. Returns a list
    of edge points or None, if file could not be found.
    """
    if os.path.exists(edge_file):
        logging.info("Loading existing edge configuration")
        return edge_calibration.load_edge_calibration(edge_file)
    else:
        logging.info("No existing edge configuration found")
        return None


def keybindings():
    """
    Returns a list of remote keybindings as defined by
    lirc and correlated actions.
    """
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
            'KEY_SUBTITLE': ri.inc_brightness,
            'KEY_BACK': ri.reset_settings,
            'KEY_AUDIO': screenshot
    }


def calibrate_edges():
    """
    Starts the edge calibration using chromecast.
    If edge calibration fails the leds pulse red, the rambilight
    is not unpaused and no edge configuration is written to file.
    """
    global server_instance

    rambilight_instance.pause()
    ws2801.pulse()

    if server_instance is None:
        server_instance = server.init_simple_http()

    edges = edge_calibration.find_edges(stream, tv_res, led_width, led_height)

    if edges:
        ws2801.pulse()
        edge_calibration.backup_edges(edges, edge_file)
        rambilight_instance.unpause()


def calibrate_color():
    """
    Starts the color calibration using chromecast
    """
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
        ws2801.pulse()
        color_calibration.backup_calibration(calib, color_file)
        rambilight_instance.unpause()


def screenshot():
    global server_instance

    logging.info("Making screenshot.")
    if server_instance is None:
        logging.info("Starting webserver to serve image file under " + str(server.IP))
        server_instance = server.init_simple_http()

    edges = load_edges()

    img = rambilight_instance.stream.read()
    blurred = cv2.blur(img, (15,15))
    gausian_blurred = cv2.GaussianBlur(img, (13,13), 0)
    gausian_blurred_small = cv2.GaussianBlur(img, (5,5), 0)

    for blob in edges:
	blob_coords = (int(blob[0][0]), int(blob[0][1]))
        cv2.circle(img, blob_coords, 3, (255,0,0), -1)

    cv2.imwrite(server.build_file_path("screenshot.jpg"), img)
    cv2.imwrite(server.build_file_path("screenshot_blurred.jpg"), blurred)
    cv2.imwrite(server.build_file_path("screenshot_gaussian_blurred.jpg"), gausian_blurred)
    cv2.imwrite(server.build_file_path("screenshot_gaussian_blurred_small.jpg"), gausian_blurred_small)


def name():
    return "rambilight"
