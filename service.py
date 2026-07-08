from datetime import datetime
from init import db


class Service(db.Model):
    """name 即科室名称（如：牙科、眼科、全科等）"""
    __tablename__ = 'service'
    name = db.Column(db.String(100), primary_key=True, nullable=False, comment="科室名称")
    description = db.Column(db.Text, nullable=True, default="")
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0, comment="价格/元")
    state = db.Column(db.String(30), default="active", nullable=False, comment="状态:active:正常 / inactive:停用 ")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
