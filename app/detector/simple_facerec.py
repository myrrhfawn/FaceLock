import os

import cv2
import face_recognition
import numpy as np
import threading
from logging import getLogger
from fl_utils.base_logging import setup_logging
setup_logging(file_name="face_detector.log")
logger = getLogger(__name__)

IMAGE_FOLDER_PATH = "/data/FaceLock/app/detector/faces"
class SimpleFaceRec():
    def __init__(self, input_queue, output_queue=None):
        self.last_location: list = []
        self.last_landmark: list = []
        self.encoded_faces: dict = {}
        self.last_detection: list = []
        self.input_queue = input_queue
        self.output_queue = output_queue
        self.detector_thread = threading.Thread(target=self.run_detector)
        self.stop_detector = threading.Event()
        self.load_faces_from_folder()


    def prepare_image(self, image, encoding=False):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if encoding:
            image = face_recognition.face_encodings(image)
        return image

    def update_detection(self, image):
        image = self.prepare_image(image)
        self.last_location = self.get_face_location(image)
        self.last_detection = self.get_detections(image, self.last_location)
        #self.last_landmark = self.get_face_landmark(image)

    def get_face_location(self, image):
        return face_recognition.face_locations(image)

    def get_face_landmark(self, image):
        return face_recognition.face_landmarks(image)

    def get_detections(self, image, locations):
        encodings = face_recognition.face_encodings(image, locations)
        face_names = []
        logger.info(encodings)
        try:
            for encode in encodings:
                logger.info(f"encoded: {self.encoded_faces}")
                logger.info(list(self.encoded_faces.values()))
                matches = face_recognition.compare_faces(list(list(self.encoded_faces.values())), encode)
                logger.info(f"mathes: {matches}")
                name = "unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(list(self.encoded_faces.values()), encode)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    names = list(self.encoded_faces.keys())
                    name = names[best_match_index]
                face_names.append(name)
        except Exception as e:
            logger.error(f"Error during detection: {e}")
        return face_names

    def get_image_with_detection(self, image: np.array, draw: bool = False):
        if draw and len(self.last_location) > 0:
            for bbox, name in zip(self.last_location, self.last_detection):
                y1, x1, y2, x2 = bbox[0], bbox[1], bbox[2], bbox[3]
                cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 200), 4)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(image, name, (x2 + 6, y2 - 6), font, 1.0, (255, 255, 255), 1)
            #landmark = self.get_face_landmark(image)
        return image

    def start(self):
        logger.info('Detection thread started.')
        self.detector_thread.start()

    def stop(self):
        self.stop_detector.set()
        self.detector_thread.join()

    def run_detector(self):
        while not self.stop_detector.is_set():
            if not self.input_queue.empty():
                frame = self.input_queue.get()
                self.update_detection(frame)

    def load_faces_from_folder(self):
        for image_name in os.listdir(IMAGE_FOLDER_PATH):
            image_path = os.path.join(IMAGE_FOLDER_PATH, image_name)
            img = cv2.imread(image_path)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encoding = face_recognition.face_encodings(img)
            if len(encoding) > 0:
                self.encoded_faces[image_name.split(".")[0]] = encoding[0]
