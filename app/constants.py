import configparser
import ast
import os
from enum import Enum

#  pyinstaller --onefile --windowed app/main.py
# color scheme
# #00062b
# #0c004b
# #002386
# #0062d0

FACELOCK_CONFIG_PATH = "/data/my_projects/FaceLock/facelock.properties"

config_parser = configparser.ConfigParser()
config_parser.read(FACELOCK_CONFIG_PATH)

DEBUG = config_parser.getboolean("general", "debug")

MIN_DETECTION_FPS = 0

# MainWindow
REGISTER_BUTTON_TIMEOUT = 3

# FileWindow
DEFAULT_FILE_ICON_PATH = "/data/FaceLock/app/components/src/file.png"
FL_FILE_ICON_PATH = "/data/FaceLock/app/components/src/encrypted-file.png"


class Extensions(Enum):
    FL = "fl"


# SimpleFaceRec
SHOW_DETECTION = True
UNKNOWN_TITLE = "unknown"
IMAGE_FOLDER_PATH = "/data/FaceLock/app/detector/faces"

# Client
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9000

# Process resolution
RES = (854, 480)
PYRO_SERIALIZER = "pickle"

# INPUT_SOURCE = "web"
# INPUT_DEVICE = "/dev/video0"
INPUT_SOURCE = "file"
INPUT_DEVICE = "/data/my_projects/FaceLock/app/detector/biden.mp4"

MAX_FPS = 60
