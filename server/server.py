import os.path
import netifaces as ni
import SimpleHTTPServer
import SocketServer
import logging


ni.ifaddresses('eth0')
IP = ni.ifaddresses('wlan0')[2][0]['addr']

root_dir = "server_content"
URI = "http://" + IP
PORT = "8000"
server_path = URI + ":" + PORT + "/"

def init_simple_http():

    import thread,SocketServer,SimpleHTTPServer

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer((IP, int(PORT)), Handler)	

    thread.start_new_thread(httpd.serve_forever,())


def build_url(file_name):
    global server_path
    return server_path + root_dir + "/" +  file_name

def build_file_path(file_name):
    global root_dir
    return root_dir + "/" + file_name

def file_exists(file_name):
    path = build_file_path(file_name)
    return os.path.exists(path)
