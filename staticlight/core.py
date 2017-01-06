from lib import ws2801
import Adafruit_WS2801
import sys


red = 255
green = 187
blue = 0

step = 20

settings_file = "rambilight/config/staticlight_settings.pickle"

def run_program():
    ws2801.init_pixels(200)
    stored = load_settings()
    if stored is not None:
        global red, green, blue
        r,b,g = stored
        red = r
        green = g
        blue = b
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

def backup_and_set():
    backup_settings()
    set_leds()

def increase_red():
    global red
    red = inc(red)
    backup_and_set()

def decrease_red():
    global red
    red = dec(red)
    backup_and_set()

def increase_blue():
    global blue
    blue = inc(blue)
    backup_and_set()

def decrease_blue():
    global blue
    blue = dec(blue)
    backup_and_set()

def increase_green():
    global green
    green = inc(green)
    backup_and_set()

def decrease_green():
    global green
    green = dec(green)
    backup_and_set()

def inc(val):
    global step
    return min(val + step, 255)

def dec(val):
    global step
    return max(val - step, 0)


def name():
    return "staticlight"

def backup_settings():
    with open(settings_file, 'w+') as handle:
        pickle.dump((red, blue, green),
                    settings_file)

def load_settings():
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as handle:
	        return pickle.load(handle)
    else:
        return None
