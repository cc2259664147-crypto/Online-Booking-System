"""Complaint entity — from old git complaint.py, adapted for new schema."""
from datetime import datetime
from app.extensions import db


class Complaint(db.Model):
    __tablename__ = 'complaint'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('medical_service.id'), nullable=True, index=True)
    content = db.Column(db.Text, nullable=False)
    state = db.Column(db.String(30), default="pending", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'service_id', name='uq_user_service_complaint'),
    )

    user = db.relationship('AppUser', backref='complaints')
    service = db.relationship('MedicalService', backref='complaints')

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.user.username if self.user else None,
            "serviceName": self.service.name if self.service else None,
            "content": self.content,
            "state": self.state,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
