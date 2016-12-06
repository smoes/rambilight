import sys
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages/")
import imutils
import time
import io
import os.path
import cv2
import pickle
import numpy as np
import server
import logging
import sys
from server import server
from chromecast import chromecast


border_top = 90
border_left = 90


def backup_edges(edges, f):
    pickle.dump(edges, f)

def load_edge_calibration(f):
    pickle.load(f)

def calibration_image(res, coords):
    height = res[1]
    width  = res[0]
    image = np.zeros((height,width,3), np.uint8)

    circle_radius = 15

    for coord in coords:
        cv2.circle(image, coord, circle_radius, (255,255,255), -1)

    return image


def left_coords(res, num_led_height):
    height = res[1]
    width  = res[0]
    steps_height = (height - border_top * 2) / (num_led_height - 1)
    return [(border_left + circle_radius * 2, border_top + circle_radius + steps_height * i) for i in range(0, num_led_height)]


def right_coords(res, num_led_height):
    height = res[1]
    width  = res[0]
    steps_height = (height - border_top * 2) / (num_led_height - 1)
    return [(width - border_left - circle_radius, border_top + circle_radius + steps_height * i) for i in range(0, num_led_height)]



def top_coords(res, num_led_width):
    height = res[1]
    width  = res[0]
    steps_width  = (width  - border_left * 2) / (num_led_width - 1)
    return [(border_left + steps_width * i,border_top + circle_radius) for i in range(0, num_led_width)]


def bottom_coords(res, num_led_width):

    height = res[1]
    width  = res[0]
    steps_width  = (width  - border_left * 2) / (num_led_width - 1)
    return [(border_left + steps_width * i,height - border_top - circle_radius) for i in range(0, num_led_width)]



def blob_detector():
    # create a simple blob detector
    params = cv2.SimpleBlobDetector_Params()
    params.filterByArea = True
    params.minArea = 1
    params.filterByColor = 1
    params.blobColor = 255
    params.filterByCircularity = False
    params.filterByInertia = False
    params.filterByConvexity = 1
    params.minConvexity = 0.8

    return cv2.SimpleBlobDetector_create(params)


def find_edges_one_side(vs, side, calib_image, order):
    file_name = "calibration_" + side + ".jpg"
    cv2.imwrite(server.build_file_path(file_name))
    time.sleep(0.5)

    cast = chromecast.get_chromecast()
    chromcast.show_on_chromecast(server.build_url(file_name), cast)
    time.sleep(5)

    img = vs.read()
    img = cv2.fastNlMeansDenoisingColored(img,None,10,10,7,21)
    keypoints = detector.detect(img)

    coords = map(lambda kp: (kp.pt.x, kp.pt.y), keypoints)
    return order(coords)



def find_edges(vs, res, num_led_width, num_led_height):

    left_fn     = lambda points : reversed(sorted(points, key=lambda p : p[1]))
    left_coords = left_coords(res, num_led_height)
    left_img    = calibration_image(res, left_coords)
    left_name   = "left"
    left_edges  = find_edges_one_side(vs, left_name, left_img, left_fn)

    right_fn    = lambda points : sorted(points, key=lambda p : p[1])
    right_coords= right_coords(res, num_led_height)
    right_img   = calibration_image(res, right_coords)
    right_name  = "right"
    right_edges = find_edges_one_side(vs, right_name, right_img, right_fn)

    top_fn      = lambda points : sorted(points, key=lambda p : p[0])
    top_coords  = top_coords(res, num_led_width)
    top_img     = calibration_image(res, top_coords)
    top_name    = "top"
    top_edges   = find_edges_one_side(vs, top_name, top_img, top_fn)

    bottom_fn   = lambda points : reversed(sorted(points, key=lambda p : p[0]))
    bottom_coords=bottom_coords(res, num_led_width)
    bottom_img  = calibration_image(res, bottom_coords)
    bottom_name = "bottom"
    bottom_edges= fond_edges_one_side(vs, bottom_name, bottom_img, bottom_fn)

    if len(left_edges) != num_led_height:
        logger.error("Wrong number of edge blobs in left edge " +
                     "detected ("+len(left_edges)+", expected: " + num_led_height)
        sys.exit()

    if len(right_edges) != num_led_height:
        logger.error("Wrong number of edge blobs in right edge " +
                     "detected ("+len(right_edges)+", expected: " + num_led_height)
        sys.exit()

    if len(top_edges) != num_led_width:
        logger.error("Wrong number of edge blobs in top edge " +
                     "detected ("+len(top_edges)+", expected: " + num_led_width)
        sys.exit()

    if len(bottom_edges) != num_led_width:
        logger.error("Wrong number of edge blobs in bottom edge " +
                     "detected ("+len(bottom_edges)+", expected: " + num_led_width)
        sys.exit()

    all_blobs = left_edges + top_edges + right_edges + bottom_edges

    img = cv2.read()
    for blob in all_blobs:
        cv2.circle(img, coord, 5, (255,0,0), -1)

    calib_fname = "calibration.jpg"
    cv2.imwrite(server.build_file_path(calib_fname), img)
    cast = chromecast.get_chromecast()
    chromecast.show_on_chromecast(server.build_url(fname), cast);
    time.sleep(10)
    cast2.quit_app()

    with_led_num = enumerate(all_blobs)
    reverse = map(lambda enumerated: (enumerated[1], enumerated[0]), with_led_num)
    return with_led_num


def file_name(res, num_led_width, num_led_height):
    return "-".join(map(str, [res[0], res[1], num_led_width, num_led_height])) + ".jpg"
