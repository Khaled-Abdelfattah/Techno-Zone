from flask import Blueprint, request, jsonify
from models import db, Order, OrderItem, ORDER_STATUSES
from utils.jwt_utils import token_required
from utils.http_clients import get_product, validate_coupon, decrement_stock, get_cart, clear_cart

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


# ── Checkout  POST /api/orders/checkout ──────────────────────
@orders_bp.route("/checkout", methods=["POST"])
@token_required
def checkout(current_user_id, auth_token):
    data = request.get_json(silent=True) or {}

    # ----------------------------------------------------------
    # Option A: client sends cart items directly in the request
    #   { "items": [{"product_id": "p1", "qty": 2}, ...], "coupon_code": "SAVE10" }
    # Option B: Order Service fetches cart from Cart Service
    # ----------------------------------------------------------
    items_payload = data.get("items")  # list of {product_id, qty}
    coupon_code   = (data.get("coupon_code") or "").strip().upper()

    if not items_payload:
        # Fallback: fetch from Cart Service
        cart = get_cart(current_user_id, auth_token)
        if not cart or not cart.get("items"):
            return jsonify({"success": False, "message": "Cart is empty"}), 400
        items_payload = [{"product_id": i["product_id"], "qty": i["qty"]} for i in cart["items"]]

    if not items_payload:
        return jsonify({"success": False, "message": "No items to order"}), 400

    # ── Resolve products & compute subtotal ───────────────────
    resolved_items = []
    subtotal = 0.0

    for item in items_payload:
        pid = item.get("product_id")
        qty = int(item.get("qty", 1))
        if qty < 1:
            continue

        product = get_product(pid)
        if not product:
            return jsonify({"success": False, "message": f"Product '{pid}' not found or unavailable"}), 400

        unit_price = float(product["price"])
        subtotal  += unit_price * qty
        resolved_items.append({
            "product_id": pid,
            "name":       product["name"],
            "image":      product.get("image"),
            "qty":        qty,
            "unit_price": unit_price,
        })

    if not resolved_items:
        return jsonify({"success": False, "message": "No valid items"}), 400

    # ── Apply coupon ──────────────────────────────────────────
    discount      = 0.0
    coupon_id     = None
    coupon_record = None

    if coupon_code:
        coupon_record = validate_coupon(coupon_code)
        if not coupon_record:
            return jsonify({"success": False, "message": "Invalid or inactive coupon code"}), 400
        discount_pct = coupon_record.get("discount_percent", 0)
        discount     = round(subtotal * discount_pct / 100, 2)

    total = round(subtotal - discount, 2)

    # ── Persist order ─────────────────────────────────────────
    order = Order(
        user_id    = current_user_id,
        coupon_code= coupon_code if coupon_record else None,
        subtotal   = subtotal,
        discount   = discount,
        total      = total,
        status     = "pending",
    )
    db.session.add(order)
    db.session.flush()  # get order.id before committing

    for ri in resolved_items:
        db.session.add(OrderItem(
            order_id   = order.id,
            product_id = ri["product_id"],
            name       = ri["name"],
            image      = ri["image"],
            qty        = ri["qty"],
            unit_price = ri["unit_price"],
        ))

    db.session.commit()

    # ── Post-order side effects (best-effort, non-blocking) ───
    for ri in resolved_items:
        decrement_stock(ri["product_id"], ri["qty"])

    clear_cart(current_user_id, auth_token)

    return jsonify({
        "success": True,
        "message": "Order placed successfully",
        "data":    order.to_dict(include_items=True),
    }), 201


# ── List orders  GET /api/orders ─────────────────────────────
@orders_bp.route("/", methods=["GET"])
@token_required
def list_orders(current_user_id, auth_token):
    page     = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 10, type=int), 50)
    status   = request.args.get("status", "").strip()

    query = Order.query.filter_by(user_id=current_user_id)
    if status and status in ORDER_STATUSES:
        query = query.filter_by(status=status)

    pagination = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        "success": True,
        "data": {
            "orders":   [o.to_dict() for o in pagination.items],
            "total":    pagination.total,
            "page":     pagination.page,
            "pages":    pagination.pages,
        },
    }), 200


# ── Single order  GET /api/orders/<id> ───────────────────────
@orders_bp.route("/<int:order_id>", methods=["GET"])
@token_required
def get_order(order_id, current_user_id, auth_token):
    order = Order.query.filter_by(id=order_id, user_id=current_user_id).first()
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404

    return jsonify({"success": True, "data": order.to_dict(include_items=True)}), 200


# ── Update status  PATCH /api/orders/<id>/status ─────────────
# (Admin / internal — protect via API Gateway role middleware)
@orders_bp.route("/<int:order_id>/status", methods=["PATCH"])
@token_required
def update_status(order_id, current_user_id, auth_token):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404

    data   = request.get_json(silent=True) or {}
    status = (data.get("status") or "").strip().lower()

    if status not in ORDER_STATUSES:
        return jsonify({"success": False, "message": f"Invalid status. Must be one of: {', '.join(ORDER_STATUSES)}"}), 400

    order.status = status
    db.session.commit()
    return jsonify({"success": True, "data": order.to_dict(), "message": f"Order status updated to '{status}'"}), 200


# ── Cancel order  DELETE /api/orders/<id> ────────────────────
@orders_bp.route("/<int:order_id>", methods=["DELETE"])
@token_required
def cancel_order(order_id, current_user_id, auth_token):
    order = Order.query.filter_by(id=order_id, user_id=current_user_id).first()
    if not order:
        return jsonify({"success": False, "message": "Order not found"}), 404

    if order.status not in ("pending", "confirmed"):
        return jsonify({"success": False, "message": f"Cannot cancel an order with status '{order.status}'"}), 400

    order.status = "cancelled"
    db.session.commit()
    return jsonify({"success": True, "message": "Order cancelled", "data": order.to_dict()}), 200
