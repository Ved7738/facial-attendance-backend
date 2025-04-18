from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

from models import db

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key")

    db_path = os.path.join(app.instance_path, 'database.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'
    app.config['SESSION_COOKIE_SECURE'] = True

    CORS(app, supports_credentials=True, origins=["https://facial-attendance-frontend.vercel.app"])
    db.init_app(app)

    from routes.attendance import bp as attendance_bp
    from routes.admin import bp as admin_bp
    from routes.export import bp as export_bp
    from routes.admin_auth import admin_auth
    from routes.recognize import bp as recognize_bp
    from routes.add_employee import bp as add_employee_bp
    from routes.embeddings import bp as embeddings_bp

    app.register_blueprint(add_employee_bp)
    app.register_blueprint(recognize_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(export_bp)
    app.register_blueprint(admin_auth)
    app.register_blueprint(embeddings_bp)

    return app

# ✅ Make app available to gunicorn (Render looks for this)
app = create_app()

# Optional block to run locally
if __name__ == '__main__':
    with app.app_context():
        os.makedirs(app.instance_path, exist_ok=True)
        db_file = os.path.join(app.instance_path, 'database.db')
        if not os.path.exists(db_file):
            db.create_all()
            print("✅ New database created at:", db_file)
    app.run(debug=True)
