from led import rambilight
from calibration import edge_calibration
from calibration import color_calibration
from led import rambilight
from imutils.video.pivideostream import PiVideoStream
import argparse
import logging
import sys
import os
import imutils
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages/")

logging.basicConfig(level=logging.INFO)



ap = argparse.ArgumentParser()
ap.add_argument("-c", "--calibrate", type=int, default=-1,
	help="Weather the camera gets calibrated before-hand.")
args = vars(ap.parse_args())




stream = PiVideoStream(resolution=(1296, 972), framerate = 30).start()

edge_config = "config/edges.conf"

edges = []

if args["calibrate"] > 0:
    edges = edge_calibration.find_edges(stream, (1920, 1080), 25, 15)
    if args["store-calibration"] > 0:
        edge_calibration.backup_edges(edges, edge_config)
    color_calibration.calibrate(stream)
else:
    if os.path.exists(edge_config):
        edges = edge_calibration.load_edge_calibration(edge_config)
    else:
        logging.error("No edge configuration found. Bail out.")
        sys.exit()
    color_calibration.decent_constant_calibration(stream.camera)


rambilight = RambilightDriver(1, edges, stream)
