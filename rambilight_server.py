#!/usr/bin/env python
#coding: utf8

import logging
import sys
import os
import time
import lirc
from collections import deque

from staticlight import core as staticlight_program

from rambilight.calibration import edge_calibration
from rambilight.calibration import color_calibration
from rambilight import program as rambilight_program

from lib import ws2801
from server import server

logging.basicConfig(format='[%(levelname)s][%(module)s] %(message)s', level=logging.INFO)


# turn of the lights intitially ;)
ws2801.turn_off()
ws2801.turn_off()

sockid=lirc.init("ambilight-server", blocking = False)



def power_action(current, programs):
    if current is not None:
        logging.info("Stopping " + current.name())
        current.stop_program()
    else:
        logging.info("Running rambilight light")
        programs[0].run_program()
        return programs[0]


def next_action(current, programs):
    if current is not None:
        current.stop_program()
        programs.rotate(-1)
    logging.info("Switching to " + programs[0].name())
    programs[0].run_program()
    return (programs[0], programs)


current = None
programs = deque([rambilight_program, staticlight_program])
logging.info("Rambilight server started")


while True:
    codeIR = lirc.nextcode()
    if codeIR != []:
        if codeIR[0] == "KEY_POWER": 
            current = power_action(current, programs)
        if codeIR[0] == "KEY_MENU":
            (current, programs) = next_action(current, programs)

    time.sleep(0.5)
