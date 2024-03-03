import cv2
import threading
import time
import queue
from fl_utils.base_logging import setup_logging
from logging import getLogger
from app.detector.simple_facerec import SimpleFaceRec
from app.constants import MIN_DETECTION_FPS
setup_logging(file_name="video_stream.log")
logger = getLogger(__name__)
class VideoStream():
    def __init__(self, cam_id, frame_queue):
        self.frame_queue = frame_queue
        self.detection_queue = queue.Queue()
        self.cam_id = cam_id
        self.detector = SimpleFaceRec(self.detection_queue)
        self.default_image = "/data/FaceLock/app/detector/me.jpeg"
        self.interval = 1
        self.last_detection = time.time()
        self.video_thread = threading.Thread(target=self.run_video_stream)
        self.stop_stream = threading.Event()

    def start(self):
        logger.info('Videos stream thread started.')
        self.video_thread.start()

    def stop(self):
        self.stop_stream.set()
        self.video_thread.join()

    def run_video_stream(self):
        cap = cv2.VideoCapture(self.cam_id)
        self.detector.start()
        while not self.stop_stream.is_set():
            ret, frame = cap.read()
            if ret:
                logger.info("Image from source")
                if self.detection_queue.qsize() > MIN_DETECTION_FPS:
                    with self.detection_queue.mutex:
                        self.detection_queue.queue.clear()
                self.detection_queue.put(frame)
                frame = self.detector.get_image_with_detection(frame, True)
                self.frame_queue.put({"frame": frame})
            else:
                logger.info("default image")
                frame = cv2.imread(self.default_image)
                self.frame_queue.put(frame)
        self.detector.stop()
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
