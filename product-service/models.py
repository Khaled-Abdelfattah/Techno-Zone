from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Category(db.Model):
    __tablename__ = "categories"

    id   = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(50),  nullable=False)

    products = db.relationship("Product", backref="category", lazy=True)

    def to_dict(self, include_count=False):
        d = {"id": self.id, "name": self.name, "icon": self.icon}
        if include_count:
            d["product_count"] = len(self.products)
        return d


class Product(db.Model):
    __tablename__ = "products"

    id          = db.Column(db.String(10),  primary_key=True)
    name        = db.Column(db.String(200), nullable=False)
    price       = db.Column(db.Float,       nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    image       = db.Column(db.String(255), nullable=True)
    rating      = db.Column(db.Integer,     default=0)
    badge       = db.Column(db.String(50),  nullable=True)
    stock       = db.Column(db.Integer,     default=0)
    description = db.Column(db.Text,        nullable=True)

    def to_dict(self, with_category=True):
        d = {
            "id":          self.id,
            "name":        self.name,
            "price":       self.price,
            "image":       self.image,
            "rating":      self.rating,
            "badge":       self.badge,
            "stock":       self.stock,
            "description": self.description,
        }
        if with_category and self.category:
            d["category"] = self.category.name
            d["category_id"] = self.category_id
        else:
            d["category"] = None
            d["category_id"] = self.category_id
        return d
