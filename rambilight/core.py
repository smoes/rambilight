"""
Module containing the led ambilight logic.
Although trying to program in a very functional manner,
this module is iterative programming oriented, due to performance
issues (e.g. function-call overhead in python.)
"""

from __future__ import division
import threading
import time
from lib import ws2801
import Adafruit_WS2801
import colorsys
import numpy as np
import pickle
import os
import sys
sys.path.insert(1, "/usr/local/lib/python2.7/site-packages/")
import cv2

settings_file = "rambilight/config/rambilight_settings.pickle"

class RambilightDriver(threading.Thread):

    def __init__(self, threadID, coordinates_to_led, stream):

        threading.Thread.__init__(self)
        ws2801.init_pixels(86)

        self.threadID = threadID
        self.stopped = False

        # if no coordinates are present there is no way to
        # run rambilight, so pause it.
        if coordinates_to_led:
            self.paused = False
            self.coordinates_to_led = sorted(coordinates_to_led, key=lambda t: t[1])
        else:
            self.paused = True
            self.coordinates_to_led = []
        self.stream = stream

        # Shift values, to apply color correction to the value
        # that is passed to the leds.
        # Original shift is maintained to offer reset functionality.
        # Adapt these values to your own led stripe for having a
        # decent color experience. 
        self.original_r_shift = 0.85
        self.original_b_shift = 0.63
        self.original_g_shift = 0.95

        # load existing shifts or use original
        loaded = self.load_settings()

        if loaded is not None:
            (r,g,b,brightness) = loaded
            self.r_shift = r
            self.b_shift = b
            self.g_shift = g
            self.brightness = brightness
        else:
            self.r_shift = self.original_r_shift
            self.b_shift = self.original_b_shift
            self.g_shift = self.original_g_shift
            self.brightness = 1.0


    def run(self):

        """The rambilight algorithm is optimized to be fast but also offer a smooth
        experience. Some mechanics are implemented to due technical issues
        (e.g. bright spikes in picamera pictures.). If you do not have them u may
        adapt the algorithm.

        There are three concepts to guarantee a smooth experience:

        * The algorithm is based on shift-registers containing the last n values for each
        coordinate the colors are measured for. The colors in this register are averaged
        for cleaner experience. To prevent the mentioned bright spikes in the stream
        that let the LEDs flicker, `num_outliers` outliers are ignored (biggest distance to
        previous color).

        * Actual color values are transitioned over time. This means, that a color needs
        `fade_levels` steps to actually be displayed. This mechanism makes the light-switching
        in fast changing scenes less noisy.

        * The image is blurred in spots where the colors are measured in. The blurring
        is limited to these spots. This increases the performance drastically.
        Blurring averts very small changes in color due to camera noise, that result in
        distracting background noise.

        The algorithm runs with 30-40 fps on a raspberry pi rev. 3.
        """

        shift_register_length = 5

        num_outliers = 3
        fade_levels = 5

        blur_area = 7
        blur_strength = 10

        registers = [[(255,255,255)] * shift_register_length] * len(self.coordinates_to_led)
        former_pixels = [(255,255,255)] * len(self.coordinates_to_led)

        while True:

            # check stopped/paused conditions before starting
            if self.stopped: break
            if self.paused:
                time.sleep(1)
                continue

            frame = self.stream.read()

            for (coord, led_num) in self.coordinates_to_led:

                # find the area that must be blurred and blur it.
                x_min = max(coord[1] - blur_area, 0)
                x_max = coord[1] + blur_area
                y_min = max(coord[0] - blur_area, 0)
                y_max = coord[0] + blur_area
                region = frame[x_min:x_max, y_min:y_max]
                blurred_region = cv2.blur(region, (blur_strength,blur_strength))

                # extract pixel needed
                pixel = blurred_region[blur_area][blur_area]
                r = int(pixel[2])
                g = int(pixel[1])
                b = int(pixel[0])
               

                # extract former pixel
                former_r, former_g, former_b = former_pixels[led_num]

                if r < 22 and b < 22 and g < 22 and r+b+g < 55:
                    r,g,b = (0,0,0)

                # push the new value into the shift register and find the average
                new_register = shift_elements(registers[led_num], (r,g,b)) 
                smoothed_r, smoothed_g, smoothed_b = average_without_outliers(new_register,
                                                                              num_outliers,
                                                                              (former_r, former_g, former_b))

                # calculate the step in respect of the number of fade_levels
                step_r = (smoothed_r - former_r) / fade_levels
                step_g = (smoothed_g - former_g) / fade_levels
                step_b = (smoothed_b - former_b) / fade_levels


                new_r = step_r + former_r
                new_g = step_g + former_g
                new_b = step_b + former_b


                # do the hls conversion, desaturation and brightness adjustments

                h, l, s = colorsys.rgb_to_hls(new_r/255, new_g/255, new_b/255)
                (hue, lightness, saturation) =( int(round(h * 360)), int(round(l * 100)) , int(round(s * 100)))
                new_hue = int(((100.0-(saturation * 0.15))/100.0) * saturation)
                (dh, dl, ds) = (hue, int(lightness * self.brightness), new_hue)
                r, g, b = colorsys.hls_to_rgb(dh/360, dl/100, ds/100)
                d_r, d_g, d_b = (int(round(r * 255)) ,int(round(g * 255)), int(round(b * 255)))


                shifted_r, shifted_b, shifted_g = shift_color((d_r, d_g, d_b),
                                                              (self.r_shift, self.g_shift, self.b_shift))

                output = Adafruit_WS2801.RGB_to_color(shifted_r, shifted_g, shifted_b)

                ws2801.pixels.set_pixel(led_num, output)

                # finally set the former pixel and update the register
                former_pixels[led_num] = (new_r, new_g, new_b)
                registers[led_num] = new_register
                   

            ws2801.pixels.show()


    def stop(self):
        self.stopped = True
        time.sleep(0.5)
        ws2801.turn_off()
        ws2801.turn_off()

    def pause(self):
        self.paused = True

    def unpause(self):
        self.paused = False

    def inc_factor(self, val):
        return min(val + 0.02, 1.0)

    def inc_r_shift(self):
        self.r_shift = self.inc_factor(self.r_shift)
        self.backup_settings()

    def inc_g_shift(self):
        self.g_shift = self.inc_factor(self.g_shift)
        self.backup_settings()

    def inc_b_shift(self):
        self.b_shift = self.inc_factor(self.b_shift)
        self.backup_settings()

    def inc_brightness(self):
        self.brightness = self.inc_factor(self.brightness)
        self.backup_settings()

    def dec_factor(self, val):
        return max(0.0, val - 0.02)

    def dec_r_shift(self):
        self.r_shift = self.dec_factor(self.r_shift)
        self.backup_settings()

    def dec_g_shift(self):
        self.g_shift = self.dec_factor(self.g_shift)
        self.backup_settings()

    def dec_b_shift(self):
        self.b_shift = self.dec_factor(self.b_shift)
        self.backup_settings()

    def dec_brightness(self):
        self.brightness = self.dec_factor(self.brightness)
        self.backup_settings()

    def backup_settings(self):
        with open(settings_file, 'w+') as handle:
            pickle.dump((self.r_shift, self.g_shift, self.b_shift, self.brightness), handle)

    def load_settings(self):
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as handle:
    	        return pickle.load(handle)
        return None

    def reset_settings(self):
        self.b_shift = self.original_b_shift
        self.g_shift = self.original_g_shift
        self.r_shift = self.original_r_shift
        self.brightness = 1.0
        self.backup_settings()



# Functions not accessing class members:

def shift_elements(list, element):
    """
    Shifts a new `element` in to the register `list` and returns a new register
    """
    return (list + [element])[1:]


def average_without_outliers(colors, num_outliers, reference_color):
    """
    Averages colors without taking outliers into account.
    outliers are the colors with the biggest difference to some `reference_color`
    The number of ignored outliers can be specified by `num_outliers`.
    The function returns an averaged color.
    """
    assert (num_outliers > 0)

    deltas = []
    for color in colors:
        a = reference_color
        b = color
        subtr = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
        absv = (abs(subtr[0]), abs(subtr[1]), abs(subtr[2]))
        sum = absv[0] + absv[1] + absv[2]
        deltas.append((sum, b))

    sort   = sorted(deltas, key=lambda tuple: tuple[0])
    bestn  = map(lambda tuple : tuple[1], sort)[:(-1 * num_outliers)]

    sum = (0,0,0)
    for color in bestn:
        sum = (sum[0] + color[0], sum[1] + color[1], sum[2] + color[2]) 

    n = len(bestn)
    return (int(sum[0]/n), int(sum[1]/n), int(sum[2]/2))


def s(i):
    """Returns 1 if `i` is greate then 0 -1 else"""
    return 1 if (i > 0) else -1

def shift_color(color, coeff):
    """Expects a three tuple color and a three tuple of coefficients.
    Multiplies each entry in color with a coefficient at the same index
    respectively.
    """
    return tuple(map(lambda x: int(x[0] * x[1]), zip(color, coeff)))

def convert_rgb_to_hls(r, g, b):
    h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
    return ( int(round(h * 360)), int(round(l * 100)) , int(round(s * 100)))

def convert_hls_to_rgb(h, l, s):
    r, g, b = colorsys.hls_to_rgb(h/360, l/100, s/100)
    return (int(round(r * 255)) ,int(round(g * 255)), int(round(b * 255)))
