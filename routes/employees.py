from flask import Blueprint, jsonify
from models import db, Employee

bp = Blueprint('employees', __name__)

@bp.route('/employees', methods=['GET'])
def list_employees():
    try:
        employees = Employee.query.all()
        result = [
            {
                "id": emp.id,
                "name": emp.name,
                "designation": emp.designation
            }
            for emp in employees
        ]
        return jsonify(result), 200
    except Exception as e:
        print("❌ Error fetching employees:", e)
        return jsonify({"error": str(e)}), 500
