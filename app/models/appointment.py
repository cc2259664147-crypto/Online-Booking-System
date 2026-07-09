"""Appointment entity → SQLAlchemy model."""
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
