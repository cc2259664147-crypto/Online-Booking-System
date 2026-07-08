from datetime import datetime
from init import db


class Review(db.Model):
    """评论区 — 公开评论，所有人可见，不绑定到具体服务"""
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    comment = db.Column(db.Text, nullable=True, default="", comment="评论内容")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
