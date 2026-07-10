"""Coupon entity → SQLAlchemy model."""
from datetime import date
from app.extensions import db


class Coupon(db.Model):
    __tablename__ = 'coupon'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    discount_amount = db.Column(db.Numeric(10, 2), nullable=False)
    valid_until = db.Column(db.Date, nullable=False)
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "discountAmount": str(self.discount_amount),
            "validUntil": self.valid_until.isoformat() if self.valid_until else None,
            "active": self.active,
        }
