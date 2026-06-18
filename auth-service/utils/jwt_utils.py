import os
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify

SECRET_KEY    = os.getenv("SECRET_KEY", "change-me")
ALGORITHM     = "HS256"
ACCESS_EXPIRY = int(os.getenv("ACCESS_TOKEN_EXPIRY_HOURS", 24))


def generate_token(user_id: int) -> str:
    """Issue a signed JWT for the given user_id."""
    payload = {
        "sub": user_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=ACCESS_EXPIRY),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT. Raises jwt.ExpiredSignatureError or jwt.InvalidTokenError."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def token_required(f):
    """Decorator — protects a route; injects current_user_id into kwargs."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"success": False, "message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"success": False, "message": "Invalid token"}), 401
        kwargs["current_user_id"] = payload["sub"]
        return f(*args, **kwargs)
    return decorated
