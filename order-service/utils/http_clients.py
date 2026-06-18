"""
HTTP client helpers for calling sibling microservices.
URLs are read from environment variables so they work in both
local Docker Compose and production (Kubernetes / ECS).
"""
import os
import requests

PRODUCT_SERVICE_URL = os.getenv("PRODUCT_SERVICE_URL", "http://localhost:3002")
COUPON_SERVICE_URL  = os.getenv("COUPON_SERVICE_URL",  "http://localhost:3007")
CART_SERVICE_URL    = os.getenv("CART_SERVICE_URL",    "http://localhost:3004")

_TIMEOUT = 5  # seconds


def get_product(product_id: str) -> dict | None:
    """Fetch a product from Product Service. Returns dict or None on failure."""
    try:
        r = requests.get(f"{PRODUCT_SERVICE_URL}/api/products/{product_id}", timeout=_TIMEOUT)
        if r.status_code == 200:
            return r.json().get("data")
    except requests.RequestException:
        pass
    return None


def validate_coupon(code: str) -> dict | None:
    """
    Validate a coupon code via Coupon Service.
    Returns {"code": ..., "discount_percent": ...} or None if invalid.
    """
    try:
        r = requests.post(
            f"{COUPON_SERVICE_URL}/api/coupon/validate",
            json={"code": code},
            timeout=_TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("data")
    except requests.RequestException:
        pass
    return None


def decrement_stock(product_id: str, qty: int) -> bool:
    """Tell Product Service to decrement stock after a successful order."""
    try:
        r = requests.patch(
            f"{PRODUCT_SERVICE_URL}/api/products/{product_id}/stock",
            json={"delta": -qty},
            timeout=_TIMEOUT,
        )
        return r.status_code == 200
    except requests.RequestException:
        return False


def get_cart(user_id: int, auth_token: str) -> dict | None:
    """Fetch cart contents from Cart Service for the given user."""
    try:
        r = requests.get(
            f"{CART_SERVICE_URL}/api/cart/",
            headers={"Authorization": f"Bearer {auth_token}", "X-User-Id": str(user_id)},
            timeout=_TIMEOUT,
        )
        if r.status_code == 200:
            return r.json().get("data")
    except requests.RequestException:
        pass
    return None


def clear_cart(user_id: int, auth_token: str) -> bool:
    """Clear the user's cart after successful checkout."""
    try:
        r = requests.delete(
            f"{CART_SERVICE_URL}/api/cart/clear",
            headers={"Authorization": f"Bearer {auth_token}", "X-User-Id": str(user_id)},
            timeout=_TIMEOUT,
        )
        return r.status_code == 200
    except requests.RequestException:
        return False
