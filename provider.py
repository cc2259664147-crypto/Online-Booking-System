from datetime import datetime
from init import db

class Provider(db.Model):
    __tablename__ = 'provider'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True, default="")
    state = db.Column(db.String(30), default="active", nullable=False, comment="状态:active:正常 / inactive:停用 ")
    number = db.Column(db.String(50), nullable=True, default="", comment="手机号")
    address = db.Column(db.String(200), nullable=True, default="", comment="地址")
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    services = db.relationship("Service", back_populates="provider")
    
    services = db.relationship("Service", back_populates="provider", cascade="all, delete-orphan", lazy="dynamic")
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "state": self.state,
            "number": self.number,
            "address": self.address,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }