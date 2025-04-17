from flask import Blueprint, request, jsonify
from deepface import DeepFace
from models import db, Employee, Attendance
from utils.iris_utils import extract_iris_embedding
from scipy.spatial.distance import cosine
import base64
import cv2
import numpy as np
import pickle

bp = Blueprint("add_face", __name__)

def decode_image(image_b64):
    nparr = np.frombuffer(base64.b64decode(image_b64), np.uint8)
    return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

@bp.route('/add-face', methods=['POST'])
def add_face():
    print("🔵 Request received at /add-face")

    data = request.get_json()
    name = data.get("name")
    image_b64 = data.get("image")

    if not name or not image_b64:
        return jsonify({"error": "Missing required fields"}), 400

    img = decode_image(image_b64)
    print("🔵 Decoding base64 image...")

    face_embed = DeepFace.represent(img, model_name='Facenet', enforce_detection=False)[0]["embedding"]

    # Iris Detection
    eyes = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml').detectMultiScale(img)
    iris_embed = None
    for (x, y, w, h) in eyes:
        eye_crop = img[y:y+h, x:x+w]
        iris_embed = extract_iris_embedding(eye_crop)
        break

    existing = Employee.query.filter_by(name=name).first()

    if existing:
        # Append new embeddings
        existing_faces = pickle.loads(existing.face_embeddings)
        existing_irises = pickle.loads(existing.iris_embeddings) if existing.iris_embeddings else []

        existing_faces.append(face_embed)
        if iris_embed is not None:
            existing_irises.append(iris_embed)

        existing.face_embeddings = pickle.dumps(existing_faces)
        existing.iris_embeddings = pickle.dumps(existing_irises)
        db.session.commit()
        return jsonify({"message": "Updated face/iris data for existing employee."})
    else:
        new_employee = Employee(
            name=name,
            face_embeddings=pickle.dumps([face_embed]),
            iris_embeddings=pickle.dumps([iris_embed]) if iris_embed is not None else None
        )
        db.session.add(new_employee)
        db.session.commit()
        return jsonify({"message": f"Face added for {name}"}), 200
