from enum import Enum

#  pyinstaller --onefile --windowed app/main.py
# color scheme
# #00062b
# #0c004b
# #002386
# #0062d0

MIN_DETECTION_FPS = 0
DEBUG = True

# MainWindow
REGISTER_BUTTON_TIMEOUT = 3

# FileWindow
# source: https://www.freepik.com/icon/encrypted-file_11327240
DEFAULT_FILE_ICON_PATH = "components/src/file_icons/file.png"
NOT_FOUND_ICON_PATH = "components/src/file_icons/not-found.png"
FL_FILE_ICON_PATH = "components/src/file_icons/encrypted-file.png"
IMAGE_FILE_ICON_PATH = "components/src/file_icons/image-file.png"
TXT_FILE_ICON_PATH = "components/src/file_icons/txt-file.png"
PDF_FILE_ICON_PATH = "components/src/file_icons/pdf-file.png"
ARCHIVE_FILE_ICON_PATH = "components/src/file_icons/archive-file.png"


class Extensions(Enum):
    FL = ("fl", FL_FILE_ICON_PATH)
    TXT = ("txt", TXT_FILE_ICON_PATH)
    PDF = ("pdf", DEFAULT_FILE_ICON_PATH)
    JPG = ("jpg", IMAGE_FILE_ICON_PATH)
    JPEG = ("jpeg", IMAGE_FILE_ICON_PATH)
    PNG = ("png", IMAGE_FILE_ICON_PATH)
    ZIP = ("zip", ARCHIVE_FILE_ICON_PATH)
    RAR = ("rar", ARCHIVE_FILE_ICON_PATH)
    UNKNOWN = ("not_found", NOT_FOUND_ICON_PATH)

    def __new__(
        cls,
        ext: str,
        icon_path: str,
    ):
        """Make possible call TrainType('confidence')"""
        obj = object.__new__(cls)
        obj._value_ = ext
        return obj

    def __init__(self, ext: str, icon_path: str):
        self._ext = ext
        self._icon_path = icon_path

    @property
    def icon_path(self) -> str:
        """Returns the icon path for the file type."""
        return self._icon_path


# SimpleFaceRec
SHOW_DETECTION = True
UNKNOWN_TITLE = "unknown"
IMAGE_FOLDER_PATH = "detector/faces"

# Client
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9001

# Process resolution
RES = (854, 480)
PYRO_SERIALIZER = "pickle"

if DEBUG:
    INPUT_SOURCE = "file"
    INPUT_DEVICE = "/data/my_projects/FaceLock/app/detector/faces/biden.mp4"
else:
    INPUT_SOURCE = "web"
    INPUT_DEVICE = "/dev/video0"

MAX_FPS = 60

# RsaCryptoProvider
KEY_STORAGE_PATH = "keys"
