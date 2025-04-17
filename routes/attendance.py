from flask import Blueprint, request, jsonify
from models import db, Attendance, Employee
from datetime import datetime

bp = Blueprint('attendance', __name__)

@bp.route('/attendance/today', methods=['GET'])
def view_today_attendance():
    try:
        today = datetime.now().date()
        records = Attendance.query.filter(
            Attendance.timestamp >= datetime.combine(today, datetime.min.time())
        ).all()

        result = []
        for record in records:
            result.append({
                "name": record.employee.name,
                "time": record.timestamp.strftime("%H:%M:%S")
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500