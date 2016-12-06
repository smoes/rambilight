import time
import logging

def decent_constant_calibration(camera):
    logging.info("Applying a well-known decent calibration.")
    camera.awb_mode = 'off'
    camera.exposure_mode = 'off'
    camera.awb_gains = (Fraction(53, 32), Fraction(9, 8))
    camera.shutter_speed = 15900


def calibrate_shutterspeed_helper(stream, references, best, current, max):
    best_speed, best_rating = best
    if(current <= max):
        stream.camera.shutter_speed = current
        time.sleep(0.4)
        img = stream.read()
        rating = rate_image(img, references)
        if rating < best_rating:
            best = (current, rating)
        return calibrate_shutterspeed_helper(stream, references, best, current + 100, max)
    else:
        return best


def calibrate_shutterspeed(stream, references):
    logging.info("Searching for best shutter-speed. This can take a while.")
    best = calibrate_shutterspeed_helper(stream, references, (-1, 99999999), 8000, 16000)
    stream.camera.shutter_speed = best[0]


def calibrate_color(stream):
    logging.info("Calibrating color using auto-calibration of camera. This can take some seconds.")
    camera = stream.camera
    camera.awb_mode='auto'
    camera.exposure_mode='auto'
    camera.iso = 400
    time.sleep(5)
    gains = stream.camera.awb_gains
    camera.awb_mode='off'
    camera.awb_gains = gains
    camera.exposure_mode='off'


def calibrate(stream):
    logging.info("Calibrating camera...")
    calibrate_color(stream)
    calibrate_shutterspeed(stream)
