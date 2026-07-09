from datetime import datetime
from init import db


class Complaint(db.Model):
    __tablename__ = 'complaint'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    service_name = db.Column(db.String(100), db.ForeignKey('service.name'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False, comment="投诉内容")
    state = db.Column(db.String(30), default="pending", nullable=False,
                      comment="状态:pending:待处理 / resolved:已解决 / rejected:已驳回")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'service_name', name='unique_user_service_complaint'),
    )
    def to_dict(self):
        return {
            
            "user_id": self.user_id,
            "service_name": self.service_name,
            "content": self.content,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
