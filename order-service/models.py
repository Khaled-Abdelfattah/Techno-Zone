from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

ORDER_STATUSES = ("pending", "confirmed", "shipped", "delivered", "cancelled")


class Order(db.Model):
    __tablename__ = "orders"

    id         = db.Column(db.Integer,  primary_key=True, autoincrement=True)
    user_id    = db.Column(db.Integer,  nullable=False, index=True)
    coupon_id  = db.Column(db.Integer,  nullable=True)
    coupon_code= db.Column(db.String(50), nullable=True)
    subtotal   = db.Column(db.Float,    nullable=False)  # before discount
    discount   = db.Column(db.Float,    default=0.0)     # amount saved
    total      = db.Column(db.Float,    nullable=False)  # after discount
    status     = db.Column(db.String(20), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship("OrderItem", backref="order", lazy=True, cascade="all, delete-orphan")

    def to_dict(self, include_items=False):
        d = {
            "id":          self.id,
            "user_id":     self.user_id,
            "coupon_code": self.coupon_code,
            "subtotal":    round(self.subtotal, 2),
            "discount":    round(self.discount, 2),
            "total":       round(self.total, 2),
            "status":      self.status,
            "created_at":  str(self.created_at),
            "item_count":  len(self.items),
        }
        if include_items:
            d["items"] = [i.to_dict() for i in self.items]
        return d


class OrderItem(db.Model):
    __tablename__ = "order_items"

    id         = db.Column(db.Integer,    primary_key=True, autoincrement=True)
    order_id   = db.Column(db.Integer,    db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.String(10), nullable=False)
    name       = db.Column(db.String(200),nullable=False)   # snapshot at time of order
    image      = db.Column(db.String(255),nullable=True)
    qty        = db.Column(db.Integer,    nullable=False, default=1)
    unit_price = db.Column(db.Float,      nullable=False)

    def to_dict(self):
        return {
            "id":         self.id,
            "product_id": self.product_id,
            "name":       self.name,
            "image":      self.image,
            "qty":        self.qty,
            "unit_price": self.unit_price,
            "subtotal":   round(self.unit_price * self.qty, 2),
        }
