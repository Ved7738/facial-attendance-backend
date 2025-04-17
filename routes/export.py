from flask import Blueprint, Response
from models import db, Employee, Attendance
import csv
import io

bp = Blueprint('export', __name__)

@bp.route("/export-attendance", methods=["GET"])
def export_attendance():
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Employee Name", "Timestamp"])

    for record in Attendance.query.join(Employee).all():
        writer.writerow([record.employee.name, record.timestamp])

    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=attendance.csv"}
    )
