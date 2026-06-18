from flask import Blueprint, request, jsonify
from models import db, Category, Product
from sqlalchemy import func

categories_bp = Blueprint("categories", __name__, url_prefix="/api/categories")


# ── List all categories  GET /api/categories ─────────────────
@categories_bp.route("/", methods=["GET"])
def list_categories():
    # Count products per category in one query
    counts = dict(
        db.session.query(Product.category_id, func.count(Product.id))
        .group_by(Product.category_id)
        .all()
    )

    categories = Category.query.order_by(Category.name).all()
    return jsonify({
        "success": True,
        "data": [c.to_dict(product_count=counts.get(c.id, 0)) for c in categories],
    }), 200


# ── Single category  GET /api/categories/<id> ────────────────
@categories_bp.route("/<int:category_id>", methods=["GET"])
def get_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"success": False, "message": "Category not found"}), 404

    count = db.session.query(func.count(Product.id)).filter(
        Product.category_id == category_id
    ).scalar()

    return jsonify({"success": True, "data": category.to_dict(product_count=count)}), 200


# ── Create category  POST /api/categories ────────────────────
@categories_bp.route("/", methods=["POST"])
def create_category():
    data = request.get_json(silent=True) or {}

    name = (data.get("name") or "").strip()
    icon = (data.get("icon") or "").strip()

    if not name or not icon:
        return jsonify({"success": False, "message": "name and icon are required"}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({"success": False, "message": "Category already exists"}), 409

    category = Category(name=name, icon=icon)
    db.session.add(category)
    db.session.commit()

    return jsonify({
        "success": True,
        "data": category.to_dict(),
        "message": "Category created",
    }), 201


# ── Update category  PATCH /api/categories/<id> ──────────────
@categories_bp.route("/<int:category_id>", methods=["PATCH"])
def update_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"success": False, "message": "Category not found"}), 404

    data = request.get_json(silent=True) or {}
    if "name" in data:
        category.name = data["name"].strip()
    if "icon" in data:
        category.icon = data["icon"].strip()

    db.session.commit()
    return jsonify({"success": True, "data": category.to_dict(), "message": "Category updated"}), 200


# ── Delete category  DELETE /api/categories/<id> ─────────────
@categories_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return jsonify({"success": False, "message": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({"success": True, "message": "Category deleted"}), 200
