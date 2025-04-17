from flask import Blueprint, request, jsonify
from deepface import DeepFace
from utils.iris_utils import extract_iris_embedding
import base64
import numpy as np
import cv2

bp = Blueprint('embeddings_bp', __name__)

def decode_base64_img(image_b64):
    try:
        print(f"📥 Raw base64 preview: {image_b64[:50]}")
        missing_padding = len(image_b64) % 4
        if missing_padding:
            image_b64 += '=' * (4 - missing_padding)
        image_data = base64.b64decode(image_b64)
        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("cv2.imdecode returned None")
        print(f"✅ Decoded image shape: {img.shape}")
        return img
    except Exception as e:
        print("❌ Failed to decode base64 image:", str(e))
        return None

@bp.route('/extract-embeddings', methods=['POST'])
def extract_embeddings():
    try:
        data = request.get_json()
        img_b64 = data.get('image')
        if not img_b64:
            return jsonify({"error": "No image provided"}), 400

        print("📅 Received base64 length:", len(img_b64))
        img = decode_base64_img(img_b64)
        if img is None:
            return jsonify({"error": "Invalid image"}), 400

        # ✅ Extract face embedding
        face_embedding = DeepFace.represent(img, model_name='Facenet', enforce_detection=False)[0]['embedding']
        face_embedding = np.array(face_embedding).astype(np.float32).tolist()  # 🧠 force clean float list

        # ✅ Extract iris embedding
        iris_embedding = None
        eyes = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml').detectMultiScale(img)
        for (x, y, w, h) in eyes:
            eye_crop = img[y:y+h, x:x+w]
            iris_embedding = extract_iris_embedding(eye_crop)
            if iris_embedding is not None:
                iris_embedding = np.array(iris_embedding).astype(np.float32).tolist()
            break

        return jsonify({
            "face_embeddings": [face_embedding],  # 🚨 Always wrap in a list
            "iris_embeddings": [iris_embedding] if iris_embedding else []
        })

    except Exception as e:
        print("❌ Error extracting embeddings:", str(e))
        return jsonify({"error": "Embedding extraction failed"}), 500
