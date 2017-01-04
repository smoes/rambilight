import ws2801
import Adafruit_WS2801
import sys


def run():
    ws2801.init_pixels(200)
    for pixel in range(0, 86):
        output = Adafruit_WS2801.RGB_to_color(0,0,0)
        ws2801.pixels.set_pixel(led_num, output)

    for pixel in range(86,200):
        output = Adafruit_WS2801.RGB_to_color(180,180,180)
        ws2801.pixels.set_pixel(led_num, output)

    ws2801.pixels.show()
    ws2801.pixels.show()

def stop():
    ws2801.turn_off()
    ws2801.turn_off()

