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
ap.add_argument("-s", "--storecalib", type=int, default=-1,
	            help="Weather newly found calibration should be stored.")
args = vars(ap.parse_args())




stream = PiVideoStream(resolution=(640, 480), framerate = 30).start()

edge_config = "config/edges.conf"

tv_res = (1920, 1080)

edges = []

if args["calibrate"] > 0:
    edges = edge_calibration.find_edges(stream, tv_res, 25, 15)

    if args["storecalib"] > 0:
        edge_calibration.backup_edges(edges, edge_config)
    color_calibration.calibrate(stream, edges)

else:
    if os.path.exists(edge_config):
        edges = edge_calibration.load_edge_calibration(edge_config)
    else:
        logging.error("No edge configuration found. Bail out.")
        sys.exit()
    color_calibration.decent_constant_calibration(stream.camera)


rambilight = RambilightDriver(1, edges, stream)
