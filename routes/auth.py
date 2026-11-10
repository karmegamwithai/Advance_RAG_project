from functools import wraps
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from services import mongodb_service

auth_bp = Blueprint("auth", __name__)

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return jsonify({"error": "Authentication required."}), 401
        return fn(*args, **kwargs)
    return wrapper

@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or len(password) < 8:
        return jsonify({"error": "Valid email and password (at least 8 characters) are required."}), 400
    if mongodb_service.users_collection.find_one({"email": email}):
        return jsonify({"error": "An account with this email already exists."}), 409

    result = mongodb_service.users_collection.insert_one({
        "email": email,
        "password_hash": generate_password_hash(password),
    })
    session.clear()
    session["user_id"] = str(result.inserted_id)
    return jsonify({"message": "Registered successfully.", "user_id": session["user_id"]}), 201

@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    user = mongodb_service.users_collection.find_one({"email": email})
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Invalid email or password."}), 401
    session.clear()
    session["user_id"] = str(user["_id"])
    return jsonify({"message": "Logged in successfully."})

@auth_bp.post("/logout")
@login_required
def logout():
    session.clear()
    return jsonify({"message": "Logged out."})

@auth_bp.get("/me")
@login_required
def me():
    return jsonify({"user_id": session["user_id"]})
