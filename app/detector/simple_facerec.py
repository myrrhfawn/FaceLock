import cv2
import face_recognition


from logging import getLogger
from fl_utils.base_logging import setup_logging
setup_logging(file_name="face_detector.log")
logger = getLogger(__name__)


class SimpleFaceRec():
    def __init__(self):
        pass

    def prepare_image(self, image, encoding=False):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        #image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
        if encoding:
            image = face_recognition.face_encodings(image)
        return image
    def get_image_with_detection(self, image, draw_location=False):
        image = self.prepare_image(image)
        loc = self.get_face_location(image)
        if draw_location and len(loc) > 0:
            for bbox in loc:
                y1, x1, y2, x2 = bbox[0], bbox[1], bbox[2], bbox[3]
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 200), 4)
        return image



    def get_face_location(self, image):

        logger.info(f"landmark: {face_recognition.face_landmarks(image)}")
        return face_recognition.face_locations(image)
