import threading
import time
from lib import ws2801
import Adafruit_WS2801
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
        if coordinates_to_led:
            self.paused = False
            self.coordinates_to_led = sorted(coordinates_to_led, key=lambda t: t[1])
        else:
            self.paused = True
            self.coordinates_to_led = []
        self.stream = stream

        self.original_r_shift = 0.85
        self.original_b_shift = 0.63
        self.original_g_shift = 0.95

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

        shift_register_length = 5
        num_aberration = 2
        fade_levels = 3
        blur_area = 8
        blur_strength = 12

        registers = [[(255,255,255)] * shift_register_length] * len(self.coordinates_to_led)
        former_pixels = [(255,255,255)] * len(self.coordinates_to_led)

        while True:

            if self.stopped: break
            if self.paused:
                time.sleep(1)
                continue

            frame = self.stream.read()

            # this could be a map over former_pixels
            for (coord, led_num) in self.coordinates_to_led:

                x_min = max(coord[1] - blur_area, 0)
                x_max = coord[1] + blur_area
                y_min = max(coord[0] - blur_area, 0)
                y_max = coord[0] + blur_area
                region = frame[x_min:x_max, y_min:y_max]
                sub_pixel = cv2.blur(region, (blur_strength,blur_strength))

                pixel = sub_pixel[blur_area][blur_area]
                r = int(pixel[2])
                g = int(pixel[1])
                b = int(pixel[0])


                former_r, former_g, former_b = former_pixels[led_num]

                new_register = shift_elements(registers[led_num], (r,g,b)) 
                smoothed_r, smoothed_g, smoothed_b = average_without_aberration(new_register, num_aberration, (former_r, former_g, former_b))

                step_r = (smoothed_r - former_r) / fade_levels
                step_g = (smoothed_g - former_g) / fade_levels
                step_b = (smoothed_b - former_b) / fade_levels

                new_r = step_r + former_r
                new_g = step_g + former_g
                new_b = step_b + former_b


                # this actually takes RBG?!
                shifted_r, shifted_b, shifted_g = shift_color((new_r, new_b, new_g), 
                                                              (self.r_shift, self.b_shift, self.g_shift))
                bn = self.brightness
                output = Adafruit_WS2801.RGB_to_color(int(shifted_r * bn),  
                                                      int(shifted_b * bn),  
                                                      int(shifted_g * bn))

                ws2801.pixels.set_pixel(led_num, output)

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


def shift_elements(list, element):
    return (list + [element])[1:]


def average_without_aberration(colors, num_aberration, old_color):
    assert (num_aberration > 0)

    average_color = old_color
    deltas = []
    for color in colors:
        a = average_color
        b = color
        subtr = (a[0] - b[0], a[1] - b[1], a[2] - b[2])
        absv = (abs(subtr[0]), abs(subtr[1]), abs(subtr[2]))
        sum = absv[0] + absv[1] + absv[2]
        deltas.append((sum, b))

    sort   = sorted(deltas, key=lambda tuple: tuple[0])
    bestn  = map(lambda tuple : tuple[1], sort)[:(-1 * num_aberration)]

    sum = (0,0,0)
    for color in bestn:
        sum = (sum[0] + color[0], sum[1] + color[1], sum[2] + color[2]) 

    n = len(bestn)
    return (int(sum[0]/n), int(sum[1]/n), int(sum[2]/2))


def s(i):
    return 1 if (i > 0) else -1

def shift_color(color, coeff):
    return tuple(map(lambda x: int(x[0] * x[1]), zip(color, coeff)))
