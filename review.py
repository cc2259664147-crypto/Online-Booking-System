from datetime import datetime
from init import db

class Review(db.Model):
    __tablename__ = 'review'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    comment = db.Column(db.Text, nullable=True, default="", comment="评论内容")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (
        db.UniqueConstraint('service_id', 'user_id', name='unique_service_user_review'),
    )
    service = db.relationship("Service", back_populates="reviews")

    def to_dict(self):
        return {
            "id": self.id,
            "service_id": self.service_id,
            "user_id": self.user_id,
            "comment": self.comment,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }