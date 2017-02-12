import os.path
import netifaces as ni
import SimpleHTTPServer
import SocketServer
import logging

root_dir = "server_content"

IP = None
URI = None
PORT = None
server_path = None

def init_simple_http():

    global IP
    global URI
    global server_path

    IP = ni.ifaddresses('wlan0')[2][0]['addr']
    URI = "http://" + IP
    PORT = "8000"
    server_path = URI + ":" + PORT + "/"


    import thread,SocketServer,SimpleHTTPServer

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
    httpd = SocketServer.TCPServer((IP, int(PORT)), Handler)	

    return thread.start_new_thread(httpd.serve_forever,())


def build_url(file_name):
    global server_path
    return server_path + root_dir + "/" +  file_name

def build_file_path(file_name):
    global root_dir
    return root_dir + "/" + file_name

def file_exists(file_name):
    path = build_file_path(file_name)
    return os.path.exists(path)
