import cv2
import base64
import requests

# 1. Get employee name dynamically
employee_name = input("Enter the employee's name: ")

# 2. Capture image
cap = cv2.VideoCapture(0)
print("📸 Press SPACE to capture the photo...")
while True:
    ret, frame = cap.read()
    cv2.imshow("Capture Face", frame)
    if cv2.waitKey(1) & 0xFF == ord(' '):  # Space key
        break

cap.release()
cv2.destroyAllWindows()

# 3. Encode to Base64
_, buffer = cv2.imencode('.jpg', frame)
img_b64 = base64.b64encode(buffer).decode('utf-8')

# 4. Send to backend
response = requests.post("http://127.0.0.1:5000/add-face", json={
    "name": employee_name,
    "image": img_b64
})

# 5. Show response
print("Status:", response.status_code)
try:
    print("Response:", response.json())
except Exception as e:
    print("Raw Response Text:", response.text)
    print("❌ Failed to decode JSON:", e)
