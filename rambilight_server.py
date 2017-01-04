#!/usr/bin/env python
#coding: utf8

from led import rambilight
from led import staticlight
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
import lirc
import time

# turn of the lights intitially ;)
ws2801.turn_off()
ws2801.turn_off()

sockid=lirc.init("ambilight-server", blocking = False)

stream = PiVideoStream(resolution=(640, 480), framerate = 30).start()
time.sleep(2)

current = None

while True:
    codeIR = lirc.nextcode()
    if codeIR[0] == "KEY_POWER":
        if current is not None:
            current[1].stop()
        else:
            current = run_rambilight()
    if codeIR[0] == "KEY_MODE":
        if current is not None:
            current[1].stop
            if current[0] == "rambilight":
                run_static_light()
            else:
                run_rambilight()

    time.sleep(0.5)


def run_rambilight():
    edges = []
    if os.path.exists(edge_config):
        logging.info("Loading existing edge configuration")
        edges = edge_calibration.load_edge_calibration(edge_config)
    else:
        sys.exit()


    edge_config = "config/edges.pickle"
    color_config = "config/colors.pickle"

    tv_res = (1920, 1080)
    led_width = 28
    led_height = 15

    edges = []

    if os.path.exists(color_config):
        logging.info("Loading existing color configuration")
        color_calibration.load_calibration(color_config, stream)
    else:
        color_calibration.decent_constant_calibration(stream.camera)


    rambilight = RambilightDriver(1, edges, stream)
    rambilight.start()
    return ("rambilight", rambilight)
