import os.path

root_dir = "server_content"
URI = "http://192.168.0.1"
PORT = "8000"
server_path = URI + ":" + PORT + "/"

def build_url(file_name):
    return server_path + file_name

def build_file_path(file_name):
    return root_dir + "/" + file_name

def file_exists(file_name):
    path = build_file_path(file_name)
    return os.path.exists(path)
