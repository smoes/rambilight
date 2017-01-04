from lib import ws2801
import Adafruit_WS2801
import sys


def run_program():
    ws2801.init_pixels(200)
    for pixel in range(0, 86):
        output = Adafruit_WS2801.RGB_to_color(0,0,0)
        ws2801.pixels.set_pixel(pixel, output)

    for pixel in range(86,200):
        color = Adafruit_WS2801.RGB_to_color(215,0,120)
        ws2801.pixels.set_pixel(pixel, color)

    ws2801.pixels.show()
    ws2801.pixels.show()

def stop_program():
    ws2801.turn_off()
    ws2801.turn_off()

def keybindings():
    return {}

def name():
    return "staticlight"
