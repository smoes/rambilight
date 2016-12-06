# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

PIXEL_COUNT = 55

SPI_PORT   = 0
SPI_DEVICE = 1
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))
