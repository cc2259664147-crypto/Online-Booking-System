from datetime import datetime
from init import db

class Complaint(db.Model):
    __tablename__ = 'complaint'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False, index=True)
    provider_id = db.Column(db.Integer, db.ForeignKey('provider.id'), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False, comment="投诉内容")
    __table_args__ = (
        db.UniqueConstraint('user_id', 'provider_id', name='unique_user_provider_complaint'),
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    state = db.Column(db.String(30), default="pending", nullable=False, comment="状态:pending:待处理 / resolved:已解决 / rejected:已驳回")
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "service_id": self.service_id,
            "content": self.content,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }