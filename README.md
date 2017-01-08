#  RAMBILIGHT - A webcam-based Raspberry Pi Ambilight Clone

This is rambilight. Rambilight is meant to enhance the TV-experience with LED-light comming from behind the TV and thereby mirroring the colors of the TV edges. Ramblight is an evening project, realized with easy to obtain parts, implemented by a functional programmer (unfortunately facing python - pardon the crappy code).

Rambilight has the following features:

1. Runs at 30-40 fps and so has only a very little delay.
2. Works with a picamera, meaning that it is input independent (not constraint to DVI inputs).
3. Offers auto detection of TV edges in the camera picture using openCV and chromecast.
4. Is comfortably controlable using a remote and lirc.
5. Is easily enhanceable using a simple program semantic (see staticlight/core.py)

Documentation tbc...