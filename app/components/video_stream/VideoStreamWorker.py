import time
from logging import getLogger

import Pyro4
from common.constants import MAX_FPS, PYRO_SERIALIZER, REGISTER_BUTTON_TIMEOUT
from common.frame import Frame
from PyQt5 import QtCore

Pyro4.config.SERIALIZER = PYRO_SERIALIZER
Pyro4.config.SERIALIZERS_ACCEPTED.add(PYRO_SERIALIZER)

logger = getLogger(__name__)
PYRO_OBJECT_URI = "PYRO:FaceDetectionPipeline@localhost:9090"


def pyro_connected(func):
    """
    Decorator to check if Pyro connection is established before executing the function.
    If not connected, it logs an error and returns None.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Pyro4.errors.CommunicationError as e:
            logger.error(f"Pyro communication error: {e}")
            return None

    return wrapper


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
        self.current_frame = Frame()

    @QtCore.pyqtSlot()
    def run(self):
        """Main loop for the video stream worker thread."""
        logger.info("Video stream thread started")
        unknown_det_time = time.time()
        try:
            while True:
                if not self.running:
                    time.sleep(1)
                    logger.info("Video stream thread is not running, sleeping...")
                    continue
                try:
                    if not self.video_stream.is_playing():
                        self.video_stream.set_state("PLAYING")
                        logger.info("Video stream set to PLAYING state")
                    if self.video_stream.is_frame_ready():
                        frame = self.video_stream.get_frame(detection=True)

                        self.frame_ready.emit(frame)
                        self.current_frame = frame

                        if (time.time() - unknown_det_time) > REGISTER_BUTTON_TIMEOUT:
                            unknown_det_time = time.time()
                        time.sleep(1 / MAX_FPS)
                except Pyro4.errors.CommunicationError as e:
                    logger.warning("Video stream thread error: {}".format(e))
                    time.sleep(1)
            logger.info("Video stream thread stopped")
        finally:
            self.stop_pipeline()

    def get_frame(self, detection: bool = False):
        """
        Returns latest frame from the video stream.
        Frame is stored as a Frame object.
        """
        return self.current_frame

    @pyro_connected
    def start_pipeline(self):
        """
        Starts the video stream pipeline.
        """
        self.running = True
        self.video_stream.set_state("PLAYING")

    @pyro_connected
    def stop_pipeline(self):
        """
        Stops the video stream pipeline.
        """
        self.running = False
        self.video_stream.set_state("PAUSED")

    @pyro_connected
    def is_playing(self):
        """Checks if the video stream is currently playing."""
        self.video_stream.is_playing()

    @pyro_connected
    def set_reload_true(self):
        """Sets the reload flag to true for the video stream."""
        self.video_stream.set_reload_true()

    def start(self):
        """Starts the video stream worker thread."""
        self.thread.start()

    def stop(self):
        """Stops the video stream worker thread and the pipeline."""
        self.stop_pipeline()
        self.thread.stop()
