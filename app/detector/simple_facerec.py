import threading
from logging import getLogger
from threading import Thread

import cv2
import face_recognition
import numpy as np
from common.client import FaceLockClient, GetEncodingsMessage
from common.constants import UNKNOWN_TITLE
from common.frame import Frame
from common.tools import prepare_image

logger = getLogger(__name__)


class SimpleFaceRec(Thread):
    def __init__(self, input_queue, output_queue=None):
        super(SimpleFaceRec, self).__init__()
        self.last_location: list = []
        self.last_landmark: list = []
        self.encoded_faces: dict = {}
        self.last_detection: list = []
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.stop_detector = threading.Event()
        self.load_faces_from_database()
        self.reload_faces = False

    def update_detection(self, frame):
        """Update the face detection for the given frame."""
        if self.reload_faces:
            self.load_faces_from_database()
        image = prepare_image(frame.img)
        self.last_location = self.get_face_location(image)
        self.last_detection = self.get_detections(image, self.last_location)
        # self.last_landmark = self.get_face_landmark(image)

    def get_face_location(self, image):
        """Get the face locations in the image."""
        return face_recognition.face_locations(image)

    def get_face_landmark(self, image):
        """Get the face landmarks in the image."""
        return face_recognition.face_landmarks(image)

    def get_detections(self, image: np.array, locations):
        """Get the face detections in the image."""
        encodings = face_recognition.face_encodings(image, locations)
        face_names = []
        # logger.info(f"enc: {encodings}")

        try:
            for encode in encodings:
                # logger.info(f"self.encoded_faces: {list(list(self.encoded_faces.values()))}")
                matches = face_recognition.compare_faces(
                    list(list(self.encoded_faces.values())), encode
                )
                name = UNKNOWN_TITLE

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(
                    list(self.encoded_faces.values()), encode
                )
                if len(face_distances) > 0:
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        names = list(self.encoded_faces.keys())
                        name = names[best_match_index]
                face_names.append(name)
                logger.info(f"names: {name}")
        except Exception as e:
            logger.error(f"Error during detection: {e}")
        return face_names

    def get_image_with_detection(self, frame: Frame, draw: bool = False) -> Frame:
        """Get the image with face detection drawn on it."""
        if draw and len(self.last_location) > 0:
            # logger.info(f"last loc: {self.last_location}")
            # logger.info(f"last det: {self.last_detection}")
            for bbox, name in zip(self.last_location, self.last_detection):
                y1, x1, y2, x2 = bbox[0], bbox[1], bbox[2], bbox[3]
                image = cv2.UMat(frame.img)

                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 200), 4)
                font = cv2.FONT_HERSHEY_DUPLEX
                # logger.info(f"name: {name}")
                cv2.putText(
                    image, name, (x2 + 6, y2 - 6), font, 1.0, (255, 255, 255), 1
                )
                frame.img = image.get()
        frame.detection = SimpleFaceRec.get_user_from_detection(self.last_detection)

        return frame

    def stop(self):
        """Stop the face detection thread."""
        self.stop_detector.set()

    def run(self):
        """Main loop for the face detection thread."""
        while not self.stop_detector.is_set():
            if not self.input_queue.empty():
                frame = self.input_queue.get()
                self.update_detection(frame)

    def load_faces_from_database(self):
        """Load face encodings from the database."""
        try:
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
                        self.encoded_faces[user["username"]] = np.frombuffer(
                            user["encode_data"]
                        )
                else:
                    logger.error("Error fetching data. No users to update")
            else:
                logger.error("Error fetching data. No users to update")

        except Exception as e:
            logger.error(f"Error fetching data. {e}")
            self.reload_faces = True
            return
        logger.info("Faces have been updated")
        self.reload_faces = False

    @staticmethod
    def get_user_from_detection(detections):
        """Get the user from the face detection."""
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
