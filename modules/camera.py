import cv2
from config.settings import CAMERA_SOURCE

def initialize_camera():
    return cv2.VideoCapture(CAMERA_SOURCE)

def read_frame(cap):
    ret, frame = cap.read()
    return ret, frame
