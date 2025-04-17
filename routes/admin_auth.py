from flask import Blueprint, request, jsonify, session

admin_auth = Blueprint('admin_auth', __name__)

# Hardcoded admin credentials (for demo)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "progility2025"

@admin_auth.route('/login', methods=['POST'])
def login():
    data = request.json
    if data['username'] == ADMIN_USERNAME and data['password'] == ADMIN_PASSWORD:
        session['is_admin'] = True
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"error": "Invalid credentials"}), 401

@admin_auth.route('/logout', methods=['POST'])
def logout():
    session.pop('is_admin', None)
    return jsonify({"message": "Logged out"})

@admin_auth.route('/is-authenticated', methods=['GET'])
def is_authenticated():
    return jsonify({"authenticated": session.get('is_admin', False)})
