from led import rambilight
from calibration import edge_calibration
from calibration import color_calibration
from led import rambilight
from imutils.video.pivideostream import PiVideoStream
from led import ws2801
from server import server
import argparse
from led.rambilight import RambilightDriver
import logging
import sys
import os
import time
import imutils
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages/")

logging.basicConfig(level=logging.INFO)



ap = argparse.ArgumentParser()
ap.add_argument("-e", "--edges", type=int, default=-1,
	help="Weather the camera gets edge calibrated before-hand.")
ap.add_argument("-c", "--color", type=int, default=-1,
	help="Weather the camera gets color calibrated before-hand.")
args = vars(ap.parse_args())

    
server.init_simple_http()

ws2801.turn_off()

stream = PiVideoStream(resolution=(640, 480), framerate = 30).start()
time.sleep(2)

edge_config = "config/edges.pickle"
color_config = "config/colors.pickle"

tv_res = (1920, 1080)
led_width = 28
led_height = 15

edges = []

if args["edges"] > 0:
    edges = edge_calibration.find_edges(stream, tv_res, led_width, led_height)
    edge_calibration.backup_edges(edges, edge_config)
else:
    if os.path.exists(edge_config):
        edges = edge_calibration.load_edge_calibration(edge_config)
    else:
        logging.error("No edge configuration found. Bail out.")
        sys.exit()

if args["color"] > 0:
    calib = color_calibration.calibrate(stream, edges, tv_res, led_width, led_height)
    color_calibration.backup_calibration(calib, color_config)
else:
    if os.path.exists(color_config):
        logging.info("Loading existing color configuration")
        color_calibration.load_calibration(color_config, stream)
    else:
        color_calibration.decent_constant_calibration(stream.camera)

rambilight = RambilightDriver(1, edges, stream)
rambilight.start()
