from flask import Blueprint, jsonify, session
from models import db, Employee, Attendance
from datetime import datetime
import pickle
from flask import request
bp = Blueprint('admin', __name__)

# 🔐 Admin-only route for listing all employees
@bp.route('/add-employee', methods=['POST'])
def add_employee():
    try:
        data = request.get_json()
        name = data.get('name')
        designation = data.get('designation')
        face_embedding = data.get('face_embeddings')
        iris_embedding = data.get('iris_embeddings')

        if not name or not face_embedding:
            return jsonify({"error": "Name or face embeddings missing"}), 400

        # Optional: Convert to numpy arrays if needed
        new_employee = Employee(
            name=name,
            designation=designation,
            face_embedding=face_embedding,
            iris_embedding=iris_embedding
        )
        db.session.add(new_employee)
        db.session.commit()

        return jsonify({"message": "Employee added"}), 200

    except Exception as e:
        print("❌ Error adding employee:", str(e))
        return jsonify({"error": "Something went wrong"}), 500

# 🔐 Admin-only route for viewing attendance logs
@bp.route("/attendance", methods=["GET"])
def get_attendance():
    if not session.get('is_admin'):
        return jsonify({"error": "Unauthorized"}), 403

    data = []
    for att in Attendance.query.order_by(Attendance.timestamp.desc()).limit(100).all():
        try:
            data.append({
                "name": att.employee.name,
                "time": att.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            })
        except Exception as e:
            print(f"❌ Error formatting attendance for employee ID {att.employee_id}: {e}")

    return jsonify(data)
