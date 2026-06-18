from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = "categories"

    id   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    icon = db.Column(db.String(50),  nullable=False)

    def to_dict(self, product_count=0):
        return {
            "id":            self.id,
            "name":          self.name,
            "icon":          self.icon,
            "product_count": product_count,
        }


class Product(db.Model):
    """
    Read-only mirror of the products table used only for counting.
    The Product Service owns writes; this service only reads category_id.
    In a fully independent deployment, replace this with an HTTP call
    to Product Service:  GET /api/products?category=<name>&per_page=0
    and use the returned `total` field.
    """
    __tablename__ = "products"

    id          = db.Column(db.String(10), primary_key=True)
    name        = db.Column(db.String(200))
    price       = db.Column(db.Float)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
