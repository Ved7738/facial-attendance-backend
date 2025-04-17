import cv2
import base64
import requests

# 1. Capture image from webcam
cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()

# 2. Convert frame to base64
_, buffer = cv2.imencode('.jpg', frame)
img_b64 = base64.b64encode(buffer).decode('utf-8')

# 3. POST to /recognize endpoint
response = requests.post("http://127.0.0.1:5000/recognize", json={
    "image": img_b64
})

# 4. Print response
print("Status:", response.status_code)
print("Response:", response.json())
