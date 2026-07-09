"""Complaint routes."""
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.complaint import Complaint
from app.models.medical_service import MedicalService
from app.utils import require_auth, require_admin, current_user

complaint_bp = Blueprint('complaints', __name__)


@complaint_bp.route('', methods=['POST'])
@require_auth
def create():
    """提交投诉 — 每个用户对每个服务只能提交一次."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    service_id = data.get('serviceId')
    content = (data.get('content') or '').strip()

    if not service_id:
        return jsonify({"error": "请指定服务"}), 400
    if not content:
        return jsonify({"error": "反馈内容不能为空"}), 400

    service = MedicalService.query.get(service_id)
    if not service:
        return jsonify({"error": "服务不存在"}), 404

    user = current_user()
    existing = Complaint.query.filter_by(user_id=user.id, service_id=service_id).first()
    if existing:
        return jsonify({"error": "你已对该服务提交过反馈，不能重复提交"}), 409

    complaint = Complaint(user_id=user.id, service_id=service_id, content=content)
    db.session.add(complaint)
    db.session.commit()
    return jsonify({"message": "反馈提交成功", "data": complaint.to_dict()}), 201


@complaint_bp.route('', methods=['GET'])
def list_complaints():
    """获取投诉列表."""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    query = Complaint.query.order_by(Complaint.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "data": [c.to_dict() for c in pagination.items],
    }), 200


@complaint_bp.route('/<int:id>', methods=['PUT'])
@require_admin
def update_state(id):
    """更新投诉状态(pending → resolved / rejected)"""
    complaint = Complaint.query.get(id)
    if not complaint:
        return jsonify({"error": "投诉不存在"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    state = data.get('state')
    if state not in ('pending', 'resolved', 'rejected'):
        return jsonify({"error": "状态只能为 pending / resolved / rejected"}), 400

    complaint.state = state
    db.session.commit()
    return jsonify({"message": "投诉状态已更新", "data": complaint.to_dict()}), 200
