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
DEFAULT_FILE_ICON_PATH = "components/src/file_icons/file.png"
NOT_FOUND_ICON_PATH = "components/src/file_icons/not-found.png"
FL_FILE_ICON_PATH = "components/src/file_icons/encrypted-file.png"


class Extensions(Enum):
    FL = ("fl", FL_FILE_ICON_PATH)
    TXT = ("txt", DEFAULT_FILE_ICON_PATH)
    PDF = ("pdf", DEFAULT_FILE_ICON_PATH)
    JPG = ("jpg", DEFAULT_FILE_ICON_PATH)
    JPEG = ("jpeg", DEFAULT_FILE_ICON_PATH)
    PNG = ("png", DEFAULT_FILE_ICON_PATH)
    ZIP = ("zip", DEFAULT_FILE_ICON_PATH)
    RAR = ("rar", DEFAULT_FILE_ICON_PATH)
    UNKNOWN = ("not_found", NOT_FOUND_ICON_PATH)

    def __new__(cls, ext: str, icon_path: str,):
        """Make possible call TrainType('confidence')"""
        obj = object.__new__(cls)
        obj._value_ = ext
        return obj

    def __init__(self, ext: str, icon_path: str):
        self._ext = ext
        self._icon_path = icon_path

    @property
    def icon_path(self) -> str:
        return self._icon_path


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
