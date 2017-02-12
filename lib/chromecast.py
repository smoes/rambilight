import pychromecast
import server
import logging

cast = None

def get_chromecast():
    global cast
    if not cast:
        chromecasts = pychromecast.get_chromecasts()
        if len(chromecasts) == 0:
            logging.error("No chromecast found!")
            return None
        cast = chromecasts[0]
        cast.wait()
    return cast

def show_on_chromecast(url, cast):
    mc = cast.media_controller
    logging.info("Displaying url " + url + " on chromecast.")
    mc.play_media(url, 'image/jpg')


def quit_app(cast):
    logging.info("Quitting app.")
    cast.quit_app()
    cast.wait()
