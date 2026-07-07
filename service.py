from datetime import datetime
from init import db

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.Integer,primary_key = True,autoincrement = True,nullable = False)
    provider_id = db.Column(db.Integer,db.ForeignKey('provider.id'),nullable = False,index = True)
    name = db.Column(db.String(100),nullable = False,index = True)
    description = db.Column(db.Text,nullable = True,default = "")
    price  = db.Column(db.Numeric(10,2),nullable = False,default = 0,comment = "价格/元")
    category = db.Column(db.String(50),nullable = False,default = "general",
                        index = True,
                        comment = "分类:geeneral:全科 / dental:牙科 /ophthalmology(眼科) / "
                        "dermatology(皮肤科) / gynecology(妇科) / pediatrics(儿科) / "
                        "orthopedics(骨科) / ENT(耳鼻喉科) /")
    state = db.Column(db.String(30),default = "active",nullable = False,comment = "状态:active:正常 / inactive:停用 ") 
    created_at = db.Column(db.DateTime, default = datetime.utcnow)
    updated_at = db.Column(db.DateTime, default = datetime.utcnow, onupdate = datetime.utcnow)
    
    provider = db.relationship("Provider",back_populates = "services")
    reviews = db.relationship("Review",back_populates = "service",cascade = "all,delete-orphan",lazy = "dynamic")
    
    def to_dict(self):
        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "name": self.name,
            "description": self.description,
            "price": str(self.price),
            "category": self.category,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }