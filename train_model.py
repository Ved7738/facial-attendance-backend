import os
import cv2
import numpy as np
import pickle
import base64
from deepface import DeepFace
from utils.iris_utils import extract_iris_embedding
from models import db, Employee
from app import create_app

app = create_app()

TRAIN_DIR = "training_data"


def get_embeddings(img_path):
    img = cv2.imread(img_path)
    if img is None:
        print(f"⚠️ Failed to load {img_path}")
        return None, None

    try:
        face_embed = DeepFace.represent(img, model_name='Facenet', enforce_detection=False)[0]['embedding']
        print(f"🔵 Face embedding extracted for {img_path}")
    except Exception as e:
        print(f"❌ Face embedding failed for {img_path}: {e}")
        return None, None

    iris_embed = None
    try:
        eyes = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml').detectMultiScale(img)
        for (x, y, w, h) in eyes:
            eye_crop = img[y:y + h, x:x + w]
            iris_embed = extract_iris_embedding(eye_crop)
            print(f"👁️ Iris embedding extracted for {img_path}")
            break
    except Exception as e:
        print(f"⚠️ Iris detection failed for {img_path}: {e}")

    return face_embed, iris_embed


def train():
    with app.app_context():
        for emp_name in os.listdir(TRAIN_DIR):
            emp_path = os.path.join(TRAIN_DIR, emp_name)
            if not os.path.isdir(emp_path):
                continue

            face_embeddings = []
            iris_embeddings = []

            for img_file in os.listdir(emp_path):
                img_path = os.path.join(emp_path, img_file)
                face_embed, iris_embed = get_embeddings(img_path)
                if face_embed is not None:
                    face_embeddings.append(face_embed)
                if iris_embed is not None:
                    iris_embeddings.append(iris_embed)

            if face_embeddings:
                existing = Employee.query.filter_by(name=emp_name).first()
                if existing:
                    existing.face_embeddings = pickle.dumps(face_embeddings)
                    existing.iris_embeddings = pickle.dumps(iris_embeddings)
                    print(f"✅ Updated {emp_name} in database")
                else:
                    new_emp = Employee(
                        name=emp_name,
                        face_embeddings=pickle.dumps(face_embeddings),
                        iris_embeddings=pickle.dumps(iris_embeddings)
                    )
                    db.session.add(new_emp)
                    print(f"🆕 Added {emp_name} to database")

        db.session.commit()
        print("✅ Training completed.")


if __name__ == "__main__":
    train()
