import threading
import ws2801
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI

class RambilightDriver(threading.Thread):
    def __init__(self, threadID, coordinates_to_led, stream):
        threading.Thread.__init__(self)
        self.threadID = threadID
        sorted_coordinates = sorted(coordinates_to_led, key=lambda t: t[1])
        self.coordinates_to_led = sorted_coordinates
	self.mode = 'light'
        self.stream = stream

    def run(self):

        former_pixels = [255,255,255] * len(coordinates_to_led)
        fade_levels = 5

        while True:

            frame = vs.read()
            frame = cv2.blur(frame, [15, 15])

            # this could be a map over former_pixels
            for (coord, led_num) in self.coordinates_to_led:
                pixel = frame[coord[0]][coord[1]]
                r = int(pixel[2])
                g = int(pixel[0])
                b = int(pixel[1])

                former_pixel = former_pixels[count]

                new_r = ((r - old_pixel[0]) / fade_levels) + old_pixel[0]
                new_g = ((g - old_pixel[1]) / fade_levels) + old_pixel[1]
                new_b = ((b - old_pixel[2]) / fade_levels) + old_pixel[2]

                output = Adafruit_WS2801.RGB_to_color(new_r,new_g,new_b) 
                ws2801.pixels.set_pixel_rgb(led_num, output)
                # maybe causing errors since no int conversion
                former_pixels[led_num] = [new_r, new_g, new_b]

                time.sleep(0.001) # not sure if needed

            ws2801.pixel.show()


    def stop(self):
        self._stop.set()
