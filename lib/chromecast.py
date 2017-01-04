import pychromecast
import server
import logging

cast = None

def get_chromecast():
    global cast
    if not cast:
        chromecasts = pychromecast.get_chromecasts_as_dict().keys()
        if len(chromecasts) == 0:
            return None
        cast = pychromecast.get_chromecast(friendly_name=chromecasts[0])
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
