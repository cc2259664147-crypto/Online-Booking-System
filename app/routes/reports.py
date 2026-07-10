"""Report routes — mirrors ReportController.java + ReportService.java."""
from flask import Blueprint, jsonify
from app.models.user import AppUser
from app.models.provider import ProviderProfile
from app.models.medical_service import MedicalService
from app.models.appointment import Appointment
from app.models.review import Review

report_bp = Blueprint('reports', __name__)


@report_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """GET /api/reports/dashboard — aggregate counts."""
    return jsonify({
        "users": AppUser.query.count(),
        "providers": ProviderProfile.query.count(),
        "services": MedicalService.query.count(),
        "appointments": Appointment.query.count(),
        "reviews": Review.query.count(),
    }), 200
