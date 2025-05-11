import numpy as np
import cv2


class Frame(object):
    def __init__(self, img: np.array = None, detection: str = None):
        self.img = img
        self.detection = detection

    def __getstate__(self):
        image = None
        if self.img is not None:
            _, encoded = cv2.imencode(
                ".jpg", self.img, [int(cv2.IMWRITE_JPEG_QUALITY), 80]
            )
            image = encoded.tobytes()
        return {
            "img": image,
            "detection": self.detection,
        }

    def __setstate__(self, state):
        image = None
        if state["img"] is not None:
            img_array = np.frombuffer(state["img"], dtype=np.uint8)
            image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        self.img = image
        self.detection = state["detection"]
