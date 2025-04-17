from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    designation = db.Column(db.String(100))
    face_embeddings = db.Column(db.PickleType)
    iris_embeddings = db.Column(db.PickleType)

    # 🔁 Relationship to Attendance
    attendance = db.relationship('Attendance', back_populates='employee', cascade='all, delete-orphan')


class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔁 Relationship back to Employee
    employee = db.relationship('Employee', back_populates='attendance')
