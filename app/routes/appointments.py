"""Appointment routes — book, cancel, list."""
from datetime import datetime
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.medical_service import MedicalService
from app.models.appointment import Appointment
from app.models.enums import AppointmentStatus
from app.utils import require_auth, current_user

appointment_bp = Blueprint('appointments', __name__)


@appointment_bp.route('', methods=['POST'])
@require_auth
def book():
    """POST /api/appointments — 预约."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    service_id = data.get('serviceId')
    time_str = data.get('appointmentTime')
    note = data.get('note')

    if not service_id or not time_str:
        return jsonify({"error": "serviceId, appointmentTime 不能为空"}), 400

    user = current_user()
    service = MedicalService.query.get(service_id)
    if not service:
        return jsonify({"error": "服务不存在"}), 400

    try:
        appointment_time = datetime.fromisoformat(time_str)
    except ValueError:
        return jsonify({"error": "appointmentTime 格式错误，请使用 ISO 格式"}), 400

    appointment = Appointment(
        user_id=user.id,
        service_id=service_id,
        appointment_time=appointment_time,
        status=AppointmentStatus.BOOKED,
        note=note,
    )
    db.session.add(appointment)
    db.session.commit()
    return jsonify({"message": "预约成功", "data": appointment.to_dict()}), 201


@appointment_bp.route('/<int:id>/cancel', methods=['POST'])
@require_auth
def cancel(id):
    """POST /api/appointments/{id}/cancel."""
    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"error": "预约不存在"}), 404

    appointment.status = AppointmentStatus.CANCELLED
    db.session.commit()
    return jsonify({"message": "预约已取消", "data": appointment.to_dict()}), 200


@appointment_bp.route('/user', methods=['GET'])
@require_auth
def my_appointments():
    """GET /api/appointments/user — 当前用户的预约列表."""
    user = current_user()
    appointments = Appointment.query.filter_by(user_id=user.id).order_by(
        Appointment.appointment_time.desc()
    ).all()
    return jsonify({"data": [a.to_dict() for a in appointments]}), 200


@appointment_bp.route('', methods=['GET'])
def all_appointments():
    """GET /api/appointments — list all."""
    appointments = Appointment.query.order_by(Appointment.appointment_time.desc()).all()
    return jsonify({"data": [a.to_dict() for a in appointments]}), 200
