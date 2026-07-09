from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    service_name = db.Column(db.String(100), nullable=False)  # 科室
    project_name = db.Column(db.String(100), nullable=False)  # 项目
    patient_name = db.Column(db.String(50), nullable=False)   # 姓名
    gender = db.Column(db.String(10), nullable=False)         # 性别
    age = db.Column(db.Integer, nullable=False)               # 年龄
    telephone = db.Column(db.String(20), nullable=False)      # 电话
    appointment_date = db.Column(db.String(20), nullable=False)  # 日期
    appointment_time = db.Column(db.String(20), nullable=False)  # 时间
    remark = db.Column(db.Text, nullable=True)                # 备注
    start_time = db.Column(db.DateTime, nullable=False)       # 开始时间
    end_time = db.Column(db.DateTime, nullable=False)         # 结束时间
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'service_name': self.service_name,
            'project_name': self.project_name,
            'patient_name': self.patient_name,
            'gender': self.gender,
            'age': self.age,
            'telephone': self.telephone,
            'appointment_date': self.appointment_date,
            'appointment_time': self.appointment_time,
            'remark': self.remark,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
