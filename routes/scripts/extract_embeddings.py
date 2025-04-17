import os, cv2, pickle
import numpy as np
from deepface import DeepFace

DATASET_DIR = "./dataset"
OUTPUT_FILE = "./embeddings.pkl"

data = {}

for person in os.listdir(DATASET_DIR):
    person_path = os.path.join(DATASET_DIR, person)
    embeddings = []
    for file in os.listdir(person_path):
        img_path = os.path.join(person_path, file)
        img = cv2.imread(img_path)
        if img is not None:
            try:
                emb = DeepFace.represent(img, model_name="Facenet", enforce_detection=False)[0]['embedding']
                embeddings.append(np.array(emb))
            except Exception as e:
                print(f"❌ Error with {img_path}: {e}")
    data[person] = embeddings

with open(OUTPUT_FILE, 'wb') as f:
    pickle.dump(data, f)

print("✅ Embeddings saved to:", OUTPUT_FILE)
