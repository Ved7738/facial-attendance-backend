from flask import Blueprint, request, jsonify
from models import db, Employee
import pickle
import numpy as np

bp = Blueprint('add_employee_bp', __name__)

@bp.route('/add-employee', methods=['POST'])
def add_employee():
    try:
        data = request.json
        name = data.get('name')
        designation = data.get('designation')
        face_embedding = data.get('face_embeddings', [])
        iris_embedding = data.get('iris_embeddings', [])

        if not name or not face_embedding:
            return jsonify({"error": "Name and face embedding required"}), 400

        # 🧠 Normalize & wrap as list of 1D numpy arrays
        face_list = [np.array(face_embedding, dtype=np.float32)]
        iris_list = [np.array(iris_embedding, dtype=np.float32)] if iris_embedding else []

        new_emp = Employee(
            name=name,
            designation=designation,
            face_embeddings=pickle.dumps(face_list),
            iris_embeddings=pickle.dumps(iris_list) if iris_list else None
        )

        db.session.add(new_emp)
        db.session.commit()

        print(f"✅ Employee saved to database: {name}")
        return jsonify({"message": "Employee added"}), 200

    except Exception as e:
        print("❌ Error saving employee:", str(e))
        return jsonify({"error": str(e)}), 500
