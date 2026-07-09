"""Appointment entity → SQLAlchemy model."""
from app.extensions import db
from app.models.enums import AppointmentStatus


class Appointment(db.Model):
    __tablename__ = 'appointment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('app_user.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('medical_service.id'), nullable=False)
    appointment_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Enum(AppointmentStatus), default=AppointmentStatus.BOOKED, nullable=False)
    note = db.Column(db.Text, nullable=True)

    user = db.relationship('AppUser', backref='appointments')
    service = db.relationship('MedicalService', backref='appointments')

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.user.username if self.user else None,
            "serviceName": self.service.name if self.service else None,
            "appointmentTime": self.appointment_time.isoformat() if self.appointment_time else None,
            "status": self.status.value if self.status else None,
            "note": self.note,
        }
