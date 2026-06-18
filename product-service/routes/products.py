from flask import Blueprint, request, jsonify
from models import db, Product, Category
from sqlalchemy import asc, desc

products_bp = Blueprint("products", __name__, url_prefix="/api/products")

ALLOWED_SORT = {
    "price_asc":  (Product.price,  asc),
    "price_desc": (Product.price,  desc),
    "rating":     (Product.rating, desc),
    "newest":     (Product.id,     desc),
}


# ── List products  GET /api/products ─────────────────────────
@products_bp.route("/", methods=["GET"])
def list_products():
    category  = request.args.get("category", "").strip()
    max_price = request.args.get("max_price", type=float)
    min_price = request.args.get("min_price", type=float)
    sort_by   = request.args.get("sort_by", "newest")
    search    = request.args.get("search", "").strip()
    page      = request.args.get("page", 1, type=int)
    per_page  = min(request.args.get("per_page", 20, type=int), 100)

    query = Product.query.join(Category, isouter=True)

    if category:
        query = query.filter(Category.name == category)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    col, direction = ALLOWED_SORT.get(sort_by, (Product.id, desc))
    query = query.order_by(direction(col))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "success": True,
        "data": {
            "products":  [p.to_dict() for p in pagination.items],
            "total":     pagination.total,
            "page":      pagination.page,
            "per_page":  pagination.per_page,
            "pages":     pagination.pages,
        },
    }), 200


# ── Single product  GET /api/products/<id> ───────────────────
@products_bp.route("/<product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404
    return jsonify({"success": True, "data": product.to_dict()}), 200


# ── Create product  POST /api/products ───────────────────────
# (Admin / internal use — protect with API Gateway auth middleware)
@products_bp.route("/", methods=["POST"])
def create_product():
    data = request.get_json(silent=True) or {}

    required = ["id", "name", "price"]
    missing  = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({"success": False, "message": f"Missing fields: {', '.join(missing)}"}), 400

    if Product.query.get(data["id"]):
        return jsonify({"success": False, "message": "Product ID already exists"}), 409

    product = Product(
        id          = data["id"],
        name        = data["name"],
        price       = float(data["price"]),
        category_id = data.get("category_id"),
        image       = data.get("image"),
        rating      = int(data.get("rating", 0)),
        badge       = data.get("badge"),
        stock       = int(data.get("stock", 0)),
        description = data.get("description"),
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({"success": True, "data": product.to_dict(), "message": "Product created"}), 201


# ── Update product  PATCH /api/products/<id> ─────────────────
@products_bp.route("/<product_id>", methods=["PATCH"])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404

    data = request.get_json(silent=True) or {}
    updatable = ["name", "price", "category_id", "image", "rating", "badge", "stock", "description"]
    for field in updatable:
        if field in data:
            setattr(product, field, data[field])

    db.session.commit()
    return jsonify({"success": True, "data": product.to_dict(), "message": "Product updated"}), 200


# ── Delete product  DELETE /api/products/<id> ────────────────
@products_bp.route("/<product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"success": True, "message": "Product deleted"}), 200


# ── Decrement stock  PATCH /api/products/<id>/stock ──────────
# Called internally by Order Service after successful checkout
@products_bp.route("/<product_id>/stock", methods=["PATCH"])
def update_stock(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404

    data = request.get_json(silent=True) or {}
    delta = int(data.get("delta", 0))  # negative to decrement, positive to restock

    new_stock = product.stock + delta
    if new_stock < 0:
        return jsonify({"success": False, "message": "Insufficient stock"}), 400

    product.stock = new_stock
    db.session.commit()
    return jsonify({"success": True, "data": {"stock": product.stock}}), 200
