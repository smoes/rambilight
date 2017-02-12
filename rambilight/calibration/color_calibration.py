import time
import math
import pickle
from lib import server
from lib import chromecast
import sys
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages/")
import cv2
import numpy as np
import logging
from simple_value_object import ValueObject

class ColorCoordinatesReference(ValueObject):
    def __init__(self, x, y, color, weight):
        pass

def decent_constant_calibration(camera):
    logging.info("Applying a well-known decent calibration.")
    camera.awb_mode = 'off'
    camera.exposure_mode = 'off'
    camera.awb_gains = (Fraction(53, 32), Fraction(9, 8))
    camera.shutter_speed = 20000

def backup_calibration(calib, f):
    logging.info("Writing color backup to " + str(f))
    with open(f, 'w+') as handle:
        pickle.dump(calib, handle)

def load_calibration(f, stream):
    logging.info("Loading and applying color backup from " + str(f))
    with open(f, 'r') as handle:
    	load_calibration_helper(pickle.load(handle), stream)

def load_calibration_helper(params, stream):
    camera = stream.camera
    logging.info("Applying a stored calibration.")
    (gains, shutter) = params
    camera.awb_mode = 'off'
    camera.exposure_mode = 'off'
    camera.iso = 1600
    camera.awb_gains = gains
    camera.shutter_speed = shutter - 3000

def score(ccr, img):
    # some number magic
    # narrow color values between 0 and 255
    # to an intervall of 0 to ~6 to not get
    # absurdly high values for exp
    narrow = 40
    rbg_pixel = img[ccr.y][ccr.x]
    cam_r = rbg_pixel[2]
    cam_g = rbg_pixel[0]
    cam_b = rbg_pixel[1]

    ccr_r = ccr.color[0]
    ccr_g = ccr.color[1]
    ccr_b = ccr.color[2]


    r = (abs (cam_r - ccr_r)) / narrow
    g = (abs (cam_g - ccr_g)) / narrow
    b = (abs (cam_b - ccr_b)) / narrow

    return sum(map(math.exp, [r,g,b])) * ccr.weight

def rate_image(image, ccrs):
    return sum([score(ccr, image) for ccr in ccrs])

def calibrate_shutterspeed_helper(stream, references, best, current, max):
    best_speed, best_rating = best
    if(current <= max):
        stream.camera.shutter_speed = current
        time.sleep(0.4)
        img = stream.read()
        rating = rate_image(img, references)
        if rating < best_rating:
            best = (current - 2000, rating)
        return calibrate_shutterspeed_helper(stream, references, best, current + 100, max)
    else:
        return best


def calibrate_shutterspeed(stream, references):
    logging.info("Searching for best shutter-speed. This can take a while.")
    best = calibrate_shutterspeed_helper(stream, references, (-1, 99999999), 8000, 16000)
    stream.camera.shutter_speed = best[0]
    return best[0]


def calibrate_color(stream):
    logging.info("Calibrating color using auto-calibration of camera. This can take some seconds.")
    camera = stream.camera
    camera.awb_mode='auto'
    camera.exposure_mode='auto'
    camera.iso = 1600
    time.sleep(8)
    gains = stream.camera.awb_gains
    camera.awb_mode='off'
    camera.awb_gains = gains
    camera.exposure_mode='off'
    return gains


def generate_calibration_data(tv_res, edges, led_width, led_height):
    edges = map(lambda edge : edge[0], edges)
    (width, height) = tv_res
    center = (int(width/2), int(height/2))
    (half_width, half_height) = center

    image = np.zeros((height,width,3), np.uint8)

    bgr_red    = (0,0,255)
    red = (255,0,0)
    bgr_blue   = (255,0,0)
    blue = (0, 0, 255)
    bgr_green  = (0,255,0)
    green = bgr_green
    bgr_yellow = (0,255,255)
    yellow = (255,255,0)
    white  = (255,255,255)

    cv2.rectangle(image, (0,0), center, bgr_red, -1)
    cv2.rectangle(image, (half_width,0), (width, half_height), bgr_blue, -1)
    cv2.rectangle(image, (0,half_height), (half_width, height), bgr_green, -1)
    cv2.rectangle(image, (half_width, half_height), (width, height), bgr_yellow, -1)

    center_rect_start= (half_width - (half_width/2), half_height - (half_height/2))
    center_rect_end  = (half_width + (half_width/2),half_height + (half_height/2))
    cv2.rectangle(image, center_rect_start, center_rect_end, white, -1)

    left = edges[:led_height]
    top = edges[led_height:(led_height + led_width)]
    right = edges[(led_height + led_width):(led_height * 2 + led_width)]
    bottom = edges[(led_height * 2 + led_width):(led_height * 2 + led_width * 2)]


    lh = int(round(led_height/2))
    lw = int(round(led_width/2))
    left_bot = [ColorCoordinatesReference(c[0], c[1], green, 1) for c in left[:lh]]
    left_top = [ColorCoordinatesReference(c[0], c[1], red, 1) for c in left[(lh+1):]]
    left_cc = left_bot + left_top

    top_left = [ColorCoordinatesReference(c[0], c[1], red, 1) for c in left[:lw]]
    top_right= [ColorCoordinatesReference(c[0], c[1], blue, 1) for c in left[(lw+1):]]
    top_cc = top_left + top_right

    right_top= [ColorCoordinatesReference(c[0], c[1], blue, 1) for c in right[:lh]]
    right_bot= [ColorCoordinatesReference(c[0], c[1],yellow, 1) for c in right[(lh+1):]]
    right_cc = right_top + right_bot

    bot_right= [ColorCoordinatesReference(c[0], c[1],yellow, 1) for c in right[:lw]]
    bot_left = [ColorCoordinatesReference(c[0], c[1],green, 1) for c in right[(lw+1):]]
    bot_cc = bot_right + bot_left

    a = left[lh]
    b = right[lh]
    white_x = (a[0] + b[0])/2
    white_y = (a[1] + b[1])/2
    white_cc = ColorCoordinatesReference(white_x, white_y, white, 100)

    logging.info(str(left[1]))

    return (image, left_cc + top_cc + right_cc + bot_cc + [white_cc])



def calibrate(stream, edges, tv_res, led_width, led_height):
    logging.info("Calibrating camera color...")
    (img, ccs) = generate_calibration_data(tv_res, edges, led_width, led_height)

    calibimg_name = "color_calibration.jpg"
    cv2.imwrite(server.build_file_path(calibimg_name), img)
    time.sleep(0.5)

    cast = chromecast.get_chromecast()
    cast.quit_app()
    chromecast.show_on_chromecast(server.build_url(calibimg_name), cast)

    gains = calibrate_color(stream)
    return (gains, calibrate_shutterspeed(stream, ccs))

