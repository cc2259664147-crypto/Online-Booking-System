"""Review entity → SQLAlchemy model."""
from datetime import datetime
from app.extensions import db


class Review(db.Model):
    __tablename__ = 'review'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('medical_service.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('AppUser', backref='reviews')
    service = db.relationship('MedicalService', backref='reviews')

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.user.username if self.user else None,
            "serviceName": self.service.name if self.service else None,
            "rating": self.rating,
            "comment": self.comment,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
