# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

PIXEL_N = 200

pixels = []
init_pixels(PIXEL_NUM)

def turn_off():
	for i in range(0, PIXEL_COUNT):
 		color = Adafruit_WS2801.RGB_to_color(0,0,0)
		pixels.set_pixel(i, color)
	pixels.show()


def init_pixels(num):
    global pixels
    SPI_PORT   = 0
    SPI_DEVICE = 1
    pixels = Adafruit_WS2801.WS2801Pixels(num, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
