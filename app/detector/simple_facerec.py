import os
import threading
from logging import getLogger
from threading import Thread

import cv2
import dlib
import numpy as np
from common.client import FaceLockClient, GetEncodingsMessage
from common.constants import UNKNOWN_TITLE
from common.frame import Frame

logger = getLogger(__name__)

# Load dlib models once
face_detector = dlib.get_frontal_face_detector()


def get_absolute_path(relative_path):
    """Get the absolute path for a given relative path."""
    return os.path.abspath(os.path.join(os.getcwd(), relative_path))


shape_predictor = dlib.shape_predictor(
    get_absolute_path("detector/models/shape_predictor_68_face_landmarks.dat")
)
face_encoder = dlib.face_recognition_model_v1(
    get_absolute_path("detector/models/dlib_face_recognition_resnet_model_v1.dat")
)


def get_encodings(image: np.ndarray) -> list[np.ndarray]:
    """Prepares an image for face recognition using dlib."""
    rects = face_detector(image, 1)

    encodings = []
    for rect in rects:
        shape = shape_predictor(image, rect)
        encoding = np.array(face_encoder.compute_face_descriptor(image, shape))
        encodings.append(encoding)
    return encodings, rects


class SimpleFaceRec(Thread):
    def __init__(self, input_queue, output_queue=None):
        super(SimpleFaceRec, self).__init__()
        self.last_location: list = []
        self.encoded_faces: dict = {}
        self.last_detection: list = []
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.stop_detector = threading.Event()
        self.load_faces_from_database()
        self.reload_faces = False

    def update_detection(self, frame):
        """Updates the detection for the given frame."""
        if self.reload_faces:
            self.load_faces_from_database()
        self.last_detection = self.get_detections(frame.img)

    def get_detections(self, image: np.array):
        """Detects faces in the given image and returns their names."""
        face_names = []
        try:
            encodings, rects = get_encodings(image)
            self.last_location = rects

            for encode in encodings:
                matches = [
                    np.linalg.norm(known - encode) <= 0.6
                    for known in self.encoded_faces.values()
                ]
                name = UNKNOWN_TITLE
                distances = [
                    np.linalg.norm(known - encode)
                    for known in self.encoded_faces.values()
                ]
                if distances:
                    best_match_index = int(np.argmin(distances))
                    if matches[best_match_index]:
                        names = list(self.encoded_faces.keys())
                        name = names[best_match_index]
                face_names.append(name)
                logger.info(f"names: {name}")
        except Exception as e:
            logger.error(f"Error during detection: {e}")
        return face_names

    def get_image_with_detection(self, frame: Frame, draw: bool = False) -> Frame:
        """Draws the detected faces on the image."""
        if draw and len(self.last_location) > 0:
            for bbox, name in zip(self.last_location, self.last_detection):
                x1, y1, x2, y2 = bbox.left(), bbox.top(), bbox.right(), bbox.bottom()
                image = cv2.UMat(frame.img)
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 200), 4)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(
                    image, name, (x1 + 6, y1 - 6), font, 1.0, (255, 255, 255), 1
                )
                frame.img = image.get()
        frame.detection = SimpleFaceRec.get_user_from_detection(self.last_detection)
        return frame

    def stop(self):
        """Stops the face detection thread."""
        self.stop_detector.set()

    def run(self):
        """Main loop for the face detection thread."""
        while not self.stop_detector.is_set():
            if not self.input_queue.empty():
                frame = self.input_queue.get()
                self.update_detection(frame)

    def load_faces_from_database(self):
        """Loads face encodings from the database."""
        client = FaceLockClient()
        logger.info("Getting encodings from DB...")
        message = GetEncodingsMessage()
        response = client.send_message(message)
        logger.info(f"server response: {response}")
        if response and response["status"] == 200:
            users = client.get_data(response)
            self.encoded_faces = {}
            if users:
                for user in users["users"]:
                    print("_-------------_", user["encode_data"])
                    self.encoded_faces[user["username"]] = np.frombuffer(
                        user["encode_data"]
                    )
            else:
                logger.error("Error fetching data. No users to update")
        else:
            logger.error("Error fetching data. No users to update")

        try:
            pass
        except Exception as e:
            logger.error(f"Error fetching data. {e}")
            self.reload_faces = True
            return
        logger.info("Faces have been updated")
        self.reload_faces = False

    @staticmethod
    def get_user_from_detection(detections):
        """Returns the first detected user or UNKNOWN_TITLE if no user is detected."""
        user = UNKNOWN_TITLE
        for det in detections:
            if detections == user:
                continue
            return det
        return user


if __name__ == "__main__":
    import queue

    det = SimpleFaceRec(queue.Queue())
    data = det.load_faces_from_database()
