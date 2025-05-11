import time
from PyQt5 import QtCore
from app.common.base_logging import setup_logging
from logging import getLogger
from app.common.frame import Frame
from app.constants import REGISTER_BUTTON_TIMEOUT, PYRO_SERIALIZER, MAX_FPS
import Pyro4

Pyro4.config.SERIALIZER = PYRO_SERIALIZER
Pyro4.config.SERIALIZERS_ACCEPTED.add(PYRO_SERIALIZER)

setup_logging(file_name="app.log")
logger = getLogger(__name__)
PYRO_OBJECT_URI = "PYRO:FaceDetectionPipeline@localhost:9090"


class VideoStreamWorker(QtCore.QObject):
    frame_ready = QtCore.pyqtSignal(Frame)

    def __init__(self):
        super().__init__()
        self.video_stream = Pyro4.Proxy(PYRO_OBJECT_URI)
        logger.info(f"Connected to stream proxy: {PYRO_OBJECT_URI}")

        self.user_last_det = None
        self.thread = QtCore.QThread()
        self.moveToThread(self.thread)
        self.thread.started.connect(self.run)

    @QtCore.pyqtSlot()
    def run(self):
        logger.info("Video stream thread started")
        unknown_det_time = time.time()
        while self.running:
            try:
                if self.video_stream.is_frame_ready():
                    frame = self.video_stream.get_frame(detection=True)

                    self.frame_ready.emit(frame)

                    if (time.time() - unknown_det_time) > REGISTER_BUTTON_TIMEOUT:
                        unknown_det_time = time.time()
                    time.sleep(1 / MAX_FPS)
            except Pyro4.errors.CommunicationError as e:
                logger.warning("Video stream thread error: {}".format(e))
                time.sleep(1)
        logger.info("Video stream thread stopped")

    def start(self):
        self.thread.start()
        self.running = True

    def stop(self):
        self.running = False
        self.thread.stop()
