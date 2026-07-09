from datetime import datetime
from init import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False, comment="用户名")
    password = db.Column(db.String(100), nullable=False, comment="密码")
    telephone = db.Column(db.String(20), unique=True, nullable=True, comment="手机号")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    gender = db.Column(db.String(10),nullable=False)
    age = db.Column(db.Integer,nullable = False)
    
    
    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "telephone": self.telephone,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "gender": self.gender,
            "age": self.age
        }