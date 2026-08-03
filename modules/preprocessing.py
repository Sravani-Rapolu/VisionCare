import cv2
from config.settings import FRAME_WIDTH, FRAME_HEIGHT

def preprocess_frame(frame):
    frame = cv2.resize(frame, (FRAME_WIDTH, FRAME_HEIGHT))
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    return frame
