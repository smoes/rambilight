from lib import ws2801
import Adafruit_WS2801
import sys


red = 255
green = 187
blue = 0

step = 20 

def run_program():
    ws2801.init_pixels(200)
    set_leds()


def set_leds():
    for led in range(0, 86):
        output = Adafruit_WS2801.RGB_to_color(0,0,0)
        ws2801.pixels.set_pixel(led, output)

    for led in range(86,200):
        color = Adafruit_WS2801.RGB_to_color(red,blue,green)
        ws2801.pixels.set_pixel(led, color)

    ws2801.pixels.show()
    ws2801.pixels.show()


def stop_program():
    ws2801.turn_off()
    ws2801.turn_off()


def keybindings():
    return {'KEY_RIGHT': increase_red,
            'KEY_LEFT':  decrease_red,
            'KEY_UP':    increase_blue,
            'KEY_DOWN':  decrease_blue,
            'KEY_OK':    increase_green,
            'KEY_INFO':  decrease_green }


def increase_red():
    global red
    red = inc(red)
    set_leds()

def decrease_red():
    global red
    red = dec(red)
    set_leds()

def increase_blue():
    global blue
    blue = inc(blue)
    set_leds()

def decrease_blue():
    global blue
    blue = dec(blue)
    set_leds()

def increase_green():
    global green
    green = inc(green)
    set_leds()

def decrease_green():
    global green
    green = dec(green)
    set_leds()

def inc(val):
    global step
    return min(val + step, 255)

def dec(val):
    global step
    return max(val - step, 0)


def name():
    return "staticlight"
