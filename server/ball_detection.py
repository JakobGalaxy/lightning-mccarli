import numpy as np
import cv2


def detect_ball(image: np.ndarray) -> np.ndarray:
    image = cv2.GaussianBlur(image, (11, 11), 0)
    return image
