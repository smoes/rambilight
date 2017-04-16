#!/usr/bin/env python
"""
Module implementing the server managing the lirc commands
for remote control.

It contains the logic for programs and custom actions mapped to
lirc keywords.
"""

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

# set the logger
logging.basicConfig(format='[%(levelname)s][%(module)s] %(message)s',
                    level=logging.INFO)


# turn of the lights intitially ;)
ws2801.turn_off()
ws2801.turn_off()

sockid=lirc.init("ambilight-server", blocking = False)



def power_action(current, programs):
    """ Turn on and of the whole thing. """
    if current is not None:
        logging.info("Stopping " + current.name())
        current.stop_program()
    else:
        logging.info("Running rambilight light")
        programs[0].run_program()
        return programs[0]


def next_action(current, programs):
    """ Switch between programs """
    if current is not None:
        current.stop_program()
        programs.rotate(-1)
    logging.info("Switching to " + programs[0].name())
    programs[0].run_program()
    return (programs[0], programs)

def program_action(program, key):
    """ Custom actions """
    if key in program.keybindings():
        program.keybindings()[key]()

current = None

# List of all programs.
# If a new program is implemented it must be added here.
# The next_action function cycles through these programs
# in the given order (because of this, deque)
programs = deque([staticlight_program, rambilight_program])

logging.info("Rambilight server started")

# give some feedback
ws2801.pulse()
ws2801.pulse()

while True:
    codeIR = lirc.nextcode()
    if codeIR != []:
        if codeIR[0] == "KEY_POWER": 
            current = power_action(current, programs)
        elif codeIR[0] == "KEY_MENU":
            (current, programs) = next_action(current, programs)
        elif current is not None:
            program_action(current, codeIR[0])

    time.sleep(0.1)
