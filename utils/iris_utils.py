import cv2
import numpy as np

def extract_iris_embedding(eye_img):
    eye_gray = cv2.cvtColor(eye_img, cv2.COLOR_BGR2GRAY)
    eye_resized = cv2.resize(eye_gray, (64, 64))
    return eye_resized.flatten() / 255.0
