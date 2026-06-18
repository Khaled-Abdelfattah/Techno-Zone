from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User
from utils.jwt_utils import generate_token, token_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ── Register ─────────────────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name     = (data.get("name") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not name or not email or not password:
        return jsonify({"success": False, "message": "name, email and password are required"}), 400

    if len(password) < 8:
        return jsonify({"success": False, "message": "Password must be at least 8 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"success": False, "message": "Email already registered"}), 409

    user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id)
    return jsonify({
        "success": True,
        "message": "Account created successfully",
        "data": {"user": user.to_dict(), "token": token},
    }), 201


# ── Login ─────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return jsonify({"success": False, "message": "email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"success": False, "message": "Invalid email or password"}), 401

    token = generate_token(user.id)
    return jsonify({
        "success": True,
        "message": "Login successful",
        "data": {"user": user.to_dict(), "token": token},
    }), 200


# ── Me (profile) ──────────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@token_required
def me(current_user_id):
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    return jsonify({"success": True, "data": user.to_dict()}), 200


# ── Verify token (called by API Gateway / other services) ─────
@auth_bp.route("/verify", methods=["POST"])
@token_required
def verify(current_user_id):
    return jsonify({"success": True, "data": {"user_id": current_user_id}}), 200


# ── Logout (client-side — token is stateless) ─────────────────
@auth_bp.route("/logout", methods=["POST"])
def logout():
    # With JWT, logout is handled client-side by discarding the token.
    # For token invalidation, integrate a Redis deny-list here.
    return jsonify({"success": True, "message": "Logged out. Discard your token client-side."}), 200
