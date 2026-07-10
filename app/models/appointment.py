"""Appointment entity → SQLAlchemy model."""
import re
from sqlalchemy.orm import validates
from app.extensions import db
from app.models.enums import AppointmentStatus


class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    patient_name = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.BOOKED, nullable=False)
    note = db.Column(db.Text, nullable=True)

    user = db.relationship('AppUser', backref='appointments')

    @validates('phone')
    def validate_phone(self, key, phone):
        if phone is not None:
            phone = str(phone).strip()
            if not re.match(r'^1[3-9]\d{9}$', phone):
                raise ValueError("手机号必须为11位中国大陆手机号")
        return phone

    @validates('age')
    def validate_age(self, key, age):
        if age is not None:
            try:
                age = int(age)
            except (ValueError, TypeError):
                raise ValueError("年龄必须为整数")
            if age < 0 or age > 150:
                raise ValueError("年龄必须在 0-150 之间")
        return age

    def to_dict(self):
        return {
            "id": self.id,
            "serviceName": self.service_name,
            "patientName": self.patient_name,
            "gender": self.gender,
            "age": self.age,
            "phone": self.phone,
            "appointmentTime": self.appointment_time.isoformat() if self.appointment_time else None,
            "status": self.status.value if self.status else None,
            "note": self.note,
        }
