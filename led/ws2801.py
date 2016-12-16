# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

PIXEL_COUNT = 200

SPI_PORT   = 0
SPI_DEVICE = 1
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

def turn_off():
	for i in range(0, PIXEL_COUNT):
 		color = Adafruit_WS2801.RGB_to_color(0,0,0)
		pixels.set_pixel(i, color)
	pixels.show()
