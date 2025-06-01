#!/usr/bin/env python
import gi
import Pyro4

gi.require_version("Gst", "1.0")

from logging import getLogger

from common.base_logging import setup_logging
from common.constants import PYRO_SERIALIZER, SHOW_DETECTION
from detector.simple_facerec import SimpleFaceRec
from gi.repository import Gst
from stream.gstreamer_pipiline import GStreamerPipeline

setup_logging(file_name="video_pipeline.log")
logger = getLogger(__name__)

Pyro4.config.SERIALIZER = PYRO_SERIALIZER
Pyro4.config.SERIALIZERS_ACCEPTED.add(PYRO_SERIALIZER)


@Pyro4.expose
class FaceDetectionPipeline(GStreamerPipeline):
    def __init__(self):
        super().__init__()
        self.detector = SimpleFaceRec(self.detection_queue)
        self.detector.start()
        self.start()
        logger.info("Pipeline thread started.")

    def stop(self):
        """"""
        self.detector.stop()
        super().stop()

    def set_reload_true(self):
        """"""
        logger.info("SET RELOAD TRUE")
        self.detector.reload_faces = True

    def is_frame_ready(self):
        """
        Allows to check if new frame is ready to be obtained from stream.
        """

        return not (self.frame_buffer is None)

    def get_frame(self, detection: bool = False, show_det: bool = SHOW_DETECTION):
        """
        Returns latest frame from frame buffer
        Frame is stored as numpy array.

        Out:
        frame - numpy ndarray
        """
        if detection:
            ret_frame = self.detector.get_image_with_detection(
                self.frame_buffer, show_det
            )
        else:
            ret_frame = self.frame_buffer
        self.frame_buffer = None
        ret_frame.img = ret_frame.img
        return ret_frame

    def set_state(self, state: str):
        """
        Starts the feed from gstreamer pipeline.
        """
        if state == "PLAYING":
            self.player.set_state(Gst.State.PLAYING)
        elif state == "PAUSED":
            self.player.set_state(Gst.State.PAUSED)
        elif state == "NULL":
            self.player.set_state(Gst.State.PAUSED)
        else:
            logger.error(f"Unknown state: {state}. Use PLAYING, PAUSED or NULL.")
            return False

    def is_playing(self):
        """
        Returns True if pipeline is in PLAYING state.
        """
        return self.player.get_state(0)[1] == Gst.State.PLAYING


if __name__ == "__main__":
    # PYTHONPATH=$(pwd) python3 /data/my_projects/FaceLock/app/stream/video_pipeline.py
    # Init runner
    runner = FaceDetectionPipeline()

    # Create a Pyro4 daemon
    daemon = Pyro4.Daemon(host="0.0.0.0", port=9090)  # Listen 9090

    # Register the runner as a Pyro4 object
    uri = daemon.register(runner, objectId="FaceDetectionPipeline")

    logger.info(f"ModelRunner is available at: {uri}")

    # Wait for incoming requests
    daemon.requestLoop()
