import numpy as np


class Frame:
    def __init__(self, img: np.array = None, detection: str = None):
        self.img = img
        self.detection = detection
