"""
Module used to calibrate the edges (or borders) of the TV. That is,
finding the coordinates of the tv borders in camera image coordinates.

Uses openCVs SimpleBlobDetector combined with an image served by chromecast.
"""

import sys
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages/")
import cv2
import imutils
import color_calibration
import time
import io
import os.path
import pickle
import numpy as np
import logging
import sys
from lib import ws2801
from lib import server
from lib import chromecast


border_top = 160
border_left = 200


def backup_edges(edges, f):
    """
    Writes list of edges to a given file f using pickle.
    """
    logging.info("Writing edge backup to " + str(f))
    with open(f, 'w+') as handle:
       logging.info(str(edges))
       pickle.dump(edges, handle)


def load_edge_calibration(f):
    """
    Loads an existing edge calibration from a file previously
    stored using pickle.
    """
    logging.info("Loading edge backup from " + str(f))
    with open(f, 'r') as handle:
    	return pickle.load(handle)

def calibration_image(res, coords):
    """
    Creates and returns an image with a black background and white circles
    at the given coordinates.
    """
    height = res[1]
    width  = res[0]
    image = np.zeros((height,width,3), np.uint8)

    circle_radius = 15

    for coord in coords:
        cv2.circle(image, coord, circle_radius, (255,255,255), -1)

    return image


def left_coords_fn(res, num_led_height):
    """
    Returns a list of coordinates for the white circle positions in
    the calibration image, meant for calibrating the left border.
    """
    height = res[1]
    width  = res[0]
    steps_height = (height - border_top * 2) / (num_led_height - 1)
    return [(border_left, border_top + steps_height * i) for i in range(0, num_led_height)]


def right_coords_fn(res, num_led_height):
    """
    Returns a list of coordinates for the white circle positions in
    the calibration image, meant for calibrating the right border.
    """
    height = res[1]
    width  = res[0]
    steps_height = (height - border_top * 2) / (num_led_height - 1)
    return [(width - border_left, border_top + steps_height * i) for i in range(0, num_led_height)]



def top_coords_fn(res, num_led_width):
    """
    Returns a list of coordinates for the white circle positions in
    the calibration image, meant for calibrating the top border.
    """
    height = res[1]
    width  = res[0]
    steps_width  = (width  - border_left * 2) / (num_led_width - 1)
    return [(border_left + steps_width * i,border_top) for i in range(0, num_led_width)]


def bottom_coords_fn(res, num_led_width):
    """
    Returns a list of coordinates for the white circle positions in
    the calibration image, meant for calibrating the bottom border.
    """
    height = res[1]
    width  = res[0]
    steps_width  = (width  - border_left * 2) / (num_led_width - 1)
    return [(border_left + steps_width * i,height - border_top) for i in range(0, num_led_width)]



def blob_detector():
    """
    Returns a SimpleBlobDetector feasible for finding white blobs
    on a black background. Depending on the camera distance and so the
    size of the screen in the camera image, minArea must be adjusted
    """
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 2
    params.filterByColor = 1
    params.blobColor = 255
    params.filterByCircularity = False
    params.filterByInertia = False
    params.filterByConvexity = 1
    params.minConvexity = 0.3

    return cv2.SimpleBlobDetector_create(params)


def find_edges_one_side(vs, side, calib_image, order, detector):

    file_name = "calibration_" + side + ".jpg"
    file_path = server.build_file_path(file_name)
    logging.info("Writing " + side + "-calibration file to " + file_path)
    cv2.imwrite(server.build_file_path(file_name), calib_image)
    time.sleep(1.0)

    cast = chromecast.get_chromecast()
    if cast:
        cast.quit_app()
        chromecast.show_on_chromecast(server.build_url(file_name), cast)
        time.sleep(7)

    img = vs.read()
    #img = cv2.fastNlMeansDenoisingColored(img,None,10,10,7,21)
    keypoints = detector.detect(img)

    coords = map(lambda kp: (int(kp.pt[0]), int(kp.pt[1])), keypoints)
    cast.quit_app()
    cast.wait()
    return order(coords)



def find_edges(vs, res, num_led_width, num_led_height):

    detector = blob_detector()


    left_fn     = lambda points : (sorted(points, key=lambda p : p[1])[::-1])
    left_coords = left_coords_fn(res, num_led_height)
    left_img    = calibration_image(res, left_coords)
    left_name   = "left"
    left_edges  = find_edges_one_side(vs, left_name, left_img, left_fn, detector)

    right_fn    = lambda points : sorted(points, key=lambda p : p[1])
    right_coords= right_coords_fn(res, num_led_height)
    right_img   = calibration_image(res, right_coords)
    right_name  = "right"
    right_edges = find_edges_one_side(vs, right_name, right_img, right_fn, detector)

    top_fn      = lambda points : sorted(points, key=lambda p : p[0])
    top_coords  = top_coords_fn(res, num_led_width)
    top_img     = calibration_image(res, top_coords)
    top_name    = "top"
    top_edges   = find_edges_one_side(vs, top_name, top_img, top_fn, detector)

    bottom_fn   = lambda points : (sorted(points, key=lambda p : p[0])[::-1])
    bottom_coords=bottom_coords_fn(res, num_led_width)
    bottom_img  = calibration_image(res, bottom_coords)
    bottom_name = "bottom"
    bottom_edges= find_edges_one_side(vs, bottom_name, bottom_img, bottom_fn, detector)

    all_blobs = left_edges + top_edges + right_edges + bottom_edges

    img = vs.read()
    for blob in all_blobs:
	blob_coords = (int(blob[0]), int(blob[1]))
        cv2.circle(img, blob_coords, 5, (255,0,0), -1)

    calib_fname = "calibration.jpg"
    cv2.imwrite(server.build_file_path(calib_fname), img)

    cast = chromecast.get_chromecast()
    cast.quit_app()
    cast.wait()
    time.sleep(1)


    if cast:
        chromecast.show_on_chromecast(server.build_url(calib_fname), cast);
        time.sleep(10)
        cast.quit_app()
        cast.wait()


    for (t, e, n) in [("left",  left_edges,  num_led_height), 
                   ("right", right_edges, num_led_height),
                   ("top",   top_edges,   num_led_width),
                   ("bottom",bottom_edges,num_led_width)]:
        if len(e) != n:
            logging.error("Wrong number of blobs in " + t + " edge" + 
                          "(" + str(len(e)) + "/" + str(n) + ")")
            ws2801.pulse_red()
            return False

    with_led_num = enumerate(all_blobs)
    reverse = map(lambda enumerated: (enumerated[1], enumerated[0]), with_led_num)
    ws2801.pulse()
    ws2801.pulse()

    return reverse


def file_name(res, num_led_width, num_led_height):
    return "-".join(map(str, [res[0], res[1], num_led_width, num_led_height])) + ".jpg"
