"""Review routes."""
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.medical_service import MedicalService
from app.models.review import Review
from app.utils import require_auth, current_user

review_bp = Blueprint('reviews', __name__)


@review_bp.route('', methods=['POST'])
@require_auth
def create():
    """POST /api/reviews — 发表评论."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    service_id = data.get('serviceId')
    rating = data.get('rating')
    comment = data.get('comment', '').strip() or None

    if not service_id:
        return jsonify({"error": "serviceId不能为空"}), 400

    user = current_user()
    service = MedicalService.query.get(service_id)
    if not service:
        return jsonify({"error": "服务不存在"}), 400

    if rating is not None and (rating < 1 or rating > 5):
        return jsonify({"error": "评分范围为1-5"}), 400

    review = Review(
        user_id=user.id,
        service_id=service_id,
        rating=rating,
        comment=comment,
    )
    db.session.add(review)
    db.session.commit()
    return jsonify({"message": "评论发表成功", "data": review.to_dict()}), 201


@review_bp.route('', methods=['GET'])
def all_reviews():
    """GET /api/reviews — list all reviews."""
    reviews = Review.query.order_by(Review.created_at.desc()).all()
    return jsonify({"data": [r.to_dict() for r in reviews]}), 200
