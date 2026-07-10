"""Simple feedback/contact-message model for public submissions."""
from datetime import datetime
from app.extensions import db


class Feedback(db.Model):
    __tablename__ = 'feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "content": self.content,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
        }
