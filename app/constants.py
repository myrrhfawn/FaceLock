import configparser
import ast
import os
#  pyinstaller --onefile --windowed app/main.py
# color scheme
# #00062b
# #0c004b
# #002386
# #0062d0

FACELOCK_CONFIG_PATH = "/data/FaceLock/facelock.properties"

config_parser = configparser.ConfigParser()
config_parser.read(FACELOCK_CONFIG_PATH)

DEBUG = config_parser.getboolean("general", "debug")

MIN_DETECTION_FPS = 1

#SimpleFaceRec
SHOW_DETECTION = True
UNKNOWN_TITLE = "unknown"
IMAGE_FOLDER_PATH = "/data/FaceLock/app/detector/faces"
