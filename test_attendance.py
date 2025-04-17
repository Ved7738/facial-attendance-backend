import requests

response = requests.post("http://127.0.0.1:5000/attendance", json={
    "name": "John Doe"
})

print("Status:", response.status_code)
print("Response:", response.json())
