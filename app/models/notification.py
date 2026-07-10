"""Notification entity → SQLAlchemy model."""
from datetime import datetime
from app.extensions import db


class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    read_flag = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('AppUser', backref='notifications')

    def to_dict(self):
        return {
            "id": self.id,
            "userId": self.user_id,
            "title": self.title,
            "content": self.content,
            "readFlag": self.read_flag,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
