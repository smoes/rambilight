import pychromecast
import server

chromecasts = pychromecast.get_chromecasts_as_dict().keys()
cast = pychromecast.get_chromecast(friendly_name=chromecasts[0])
cast.wait()

def show_on_chromecast(url):
    mc = cast.media_controller
    logging.info("Displaying url " + url + " on chromecast.")
    mv.play_media(url, 'image/jpg')


def quit_app():
    logging.info("Quitting app.")
    cast.quit_app()
