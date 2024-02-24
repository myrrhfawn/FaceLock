import cv2
import threading

from fl_utils.base_logging import setup_logging
from logging import getLogger
from app.detector.simple_facerec import SimpleFaceRec
setup_logging(file_name="video_stream.log")
logger = getLogger(__name__)

class VideoStream():
    def __init__(self, cam_id, queue):
        self.queue = queue
        self.thread = threading.Thread(target=self.run_video_stream)
        self.cam_id = cam_id
        self.stop_stream = threading.Event()
        self.detector = SimpleFaceRec()
        self.default_image = cv2.imread("/data/FaceLock/app/detector/me.jpeg")

    def start(self):
        self.thread.start()

    def stop(self):
        self.stop_stream.set()
        self.thread.join()

    def run_video_stream(self):
        cap = cv2.VideoCapture(self.cam_id)
        while not self.stop_stream.is_set():
            ret, frame = cap.read()
            if ret:
                logger.info("Image from source")
                frame = self.detector.get_image_with_detection(frame, True)
                self.queue.put({"frame": frame})
            else:
                logger.info("default image")
                self.queue.put(self.default_image)

        cap.release()
        cv2.destroyAllWindows()

    def get_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            return ret, frame
        else:
            logger.info("Could not get frame. Using default")
            return True, self.default_image


    def isOpened(self):
        if self.cap:
            return self.cap.isOpened()
        else:
            logger.warning("Stream opened using default frame.")
            return True

    def release(self):
        self.cap.release()
