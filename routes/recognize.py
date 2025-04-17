from flask import Blueprint, request, jsonify
from deepface import DeepFace
from utils.iris_utils import extract_iris_embedding
from models import db, Employee, Attendance
from datetime import datetime
import base64
import numpy as np
import cv2
import pickle
from scipy.spatial.distance import cosine

bp = Blueprint("recognize_bp", __name__)

def decode_base64_img(image_b64):
    try:
        print(f"📥 Raw base64 preview: {image_b64[:50]}")
        image_data = base64.b64decode(image_b64)
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        print(f"✅ Decoded image shape: {img.shape}")
        return img
    except Exception as e:
        print("❌ Failed to decode image:", e)
        return None

@bp.route("/recognize", methods=["POST"])
def recognize():
    print("📌 /recognize called")

    try:
        data = request.get_json()
        image_b64 = data.get("image")

        if not image_b64:
            return jsonify({"error": "No image data provided"}), 400

        img = decode_base64_img(image_b64)
        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        face_embedding = DeepFace.represent(img, model_name="Facenet", enforce_detection=False)[0]["embedding"]
        face_embedding = np.array(face_embedding)
        print("✅ Face embedding extracted")

        iris_embedding = None
        eyes = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml').detectMultiScale(img)
        for (x, y, w, h) in eyes:
            eye_crop = img[y:y+h, x:x+w]
            iris_embedding = extract_iris_embedding(eye_crop)
            if iris_embedding is not None:
                iris_embedding = np.array(iris_embedding)
                print("✅ Iris embedding extracted")
            break

        matched_employee = None
        best_distance = float("inf")
        best_match_name = "Unknown"
        threshold = 0.6

        print("🔍 Matching with employees...")
        for emp in Employee.query.all():
            try:
                emp_faces_raw = pickle.loads(emp.face_embeddings)
                emp_face_list = emp_faces_raw if isinstance(emp_faces_raw, list) else [emp_faces_raw]

                emp_iris_list = []
                if emp.iris_embeddings:
                    emp_iris_raw = pickle.loads(emp.iris_embeddings)
                    emp_iris_list = emp_iris_raw if isinstance(emp_iris_raw, list) else [emp_iris_raw]

                for stored_face in emp_face_list:
                    stored_face = np.array(stored_face)
                    if stored_face.shape != face_embedding.shape:
                        print(f"⚠️ Shape mismatch, skipping face comparison for {emp.name}")
                        continue

                    face_distance = cosine(face_embedding, stored_face)

                    iris_distance = 0
                    if iris_embedding is not None and emp_iris_list:
                        iris_dists = []
                        for iris_vec in emp_iris_list:
                            iris_vec = np.array(iris_vec)
                            if iris_vec.shape == iris_embedding.shape:
                                iris_dists.append(cosine(iris_embedding, iris_vec))
                        iris_distance = np.mean(iris_dists) if iris_dists else 0

                    total_distance = face_distance + iris_distance

                    if total_distance < best_distance:
                        best_distance = total_distance
                        matched_employee = emp
                        best_match_name = emp.name

            except Exception as e:
                print(f"❌ Matching error for {emp.name}: {e}")

        response = {
            "name": best_match_name,
            "distance": best_distance if best_match_name != "Unknown" else float("inf"),
            "attendance": "not marked"
        }

        if best_distance <= threshold and matched_employee:
            today = datetime.now().date()
            already_marked = Attendance.query.filter(
                Attendance.employee_id == matched_employee.id,
                Attendance.timestamp >= datetime.combine(today, datetime.min.time())
            ).first()

            if not already_marked:
                db.session.add(Attendance(employee_id=matched_employee.id))
                db.session.commit()
                response["attendance"] = "marked"
            else:
                response["attendance"] = "already marked"

        print(f"✅ Recognition complete: {response}")
        return jsonify(response)

    except Exception as e:
        print("❌ Recognition failed:", e)
        return jsonify({"error": str(e)}), 500
