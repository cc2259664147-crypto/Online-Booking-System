"""MedicalService entity → SQLAlchemy model (no provider dependency)."""
from app.extensions import db


class MedicalService(db.Model):
    __tablename__ = 'medical_service'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "price": str(self.price),
            "active": self.active,
        }
