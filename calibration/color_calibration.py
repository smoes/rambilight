import time
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
    camera.shutter_speed = 15900


def score(ccr, img):
    # some number magic
    # narrow color values between 0 and 255
    # to an intervall of 0 to ~6 to not get
    # absurdly high values for exp
    narrow = 40
    rbg_pixel = img[ccr.x][ccr.y]
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
            best = (current, rating)
        return calibrate_shutterspeed_helper(stream, references, best, current + 100, max)
    else:
        return best


def calibrate_shutterspeed(stream, references):
    logging.info("Searching for best shutter-speed. This can take a while.")
    best = calibrate_shutterspeed_helper(stream, references, (-1, 99999999), 8000, 16000)
    stream.camera.shutter_speed = best[0]
    return best


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


def generate_calibration_data(tv_res, edges):
    (width, height) = tv_res
    center = (int(width/2), int(height/2))
    (half_width, half_height) = center

    image = np.zeros((height,width,3), np.uint8)

    red    = (255,0,0)
    blue   = (0,255,0)
    green  = (0,0,255)
    yellow = (255,0,255)
    white  = (255,255,255)

    cv2.rectangle(image, (0,0), center, red, 2)
    cv2.rectangle(image, (0,half_width), (half_height, width), blue, 2)
    cv2.rectangle(image, (half_height, 0), (height, half_width), green, 2)
    cv2.rectangle(image, (half_height, half_width), (height, width), yellow, 2)

    center_rect_start= (half_height - (half_height/2), half_width - (half_width/2))
    center_rect_end  = (half_height + (half_height/2), half_width + (half_width/2))
    cv2.rectangle(image, center_rect_start, center_rect_end, white, 2)

    left = edges[:15]
    top = edges[15:40]
    right = edges [40:55]
    bottom = edges [55:80]

    left_bot = [ColorCoordinatesReference(c[0], c[1], green, 1) for c in left[:7]]
    left_top = [ColorCoordinatesReference(c[0], c[1], red, 1) for c in left[8:]]
    left_cc = left_bot + left_top

    top_left = [ColorCoordinatesReference(c[0], c[1], red, 1) for c in left[:12]]
    top_right= [ColorCoordinatesReference(c[0], c[1], blue, 1) for c in left[:12]]
    top_cc = top_left + top_right

    right_top= [ColorCoordinatesReference(c[0], c[1], blue, 1) for c in right[:7]]
    right_bot= [ColorCoordinatesReference(c[0], c[1],yellow, 1) for c in right[8:]]
    right_cc = right_top + right_bot

    bot_right= [ColorCoordinatesReference(c[0], c[1],yellow, 1) for c in right[:12]]
    bot_left = [ColorCoordinatesReference(c[0], c[1],green, 1) for c in right[:12]]
    bot_cc = bot_right + bot_left

    return (img, left_cc + top_cc + right_cc + bot_cc)



def calibrate(stream, edges, tv_res):
    logging.info("Calibrating camera color...")
    (img, ccs) = generate_calibration_data(tv_res, edges)

    calibimg_name = "color_calibration.jpg"
    cv2.imwrite(server.build_file_path(calibimg_name), img)
    time.sleep(0.5)

    cast = chromecast.get_chromecast()
    cast.quit_app()
    chromecast.show_on_chromecast(server.build_url(clibimg_name), cast)

    calibrate_color(stream)
    return calibrate_shutterspeed(stream, references)

