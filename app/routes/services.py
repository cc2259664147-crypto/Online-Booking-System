"""Service routes — search, recommend, admin CRUD."""
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.medical_service import MedicalService
from app.models.review import Review
from app.utils import require_admin

service_bp = Blueprint('services', __name__)


@service_bp.route('', methods=['POST'])
@require_admin
def create():
    """POST /api/services — 管理员创建服务."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({"error": "服务名称不能为空"}), 400

    service = MedicalService(
        name=name,
        category=data.get('category', '').strip() or None,
        description=data.get('description', '').strip() or None,
        price=data.get('price', 0),
        active=True,
    )
    db.session.add(service)
    db.session.commit()
    return jsonify({"message": "服务创建成功", "data": service.to_dict()}), 201


@service_bp.route('', methods=['GET'])
def search():
    """GET /api/services?keyword= — search or list all active."""
    keyword = (request.args.get('keyword') or '').strip().lower()
    if keyword:
        results = MedicalService.query.filter(
            MedicalService.active == True,
            db.or_(
                MedicalService.name.ilike(f'%{keyword}%'),
                MedicalService.category.ilike(f'%{keyword}%'),
            )
        ).all()
    else:
        results = MedicalService.query.filter_by(active=True).all()
    return jsonify({"data": [s.to_dict() for s in results]}), 200


@service_bp.route('/recommend', methods=['GET'])
def recommend():
    """GET /api/services/recommend — top 5 active services."""
    top5 = MedicalService.query.filter_by(active=True).limit(5).all()
    return jsonify({"data": [s.to_dict() for s in top5]}), 200


# ——— 管理员服务管理 ———


@service_bp.route('/<int:id>', methods=['GET'])
def get_service(id):
    """GET /api/services/{id} — 服务详情（含评论数）"""
    service = MedicalService.query.get(id)
    if not service:
        return jsonify({"error": "服务不存在"}), 404
    result = service.to_dict()
    result['reviewCount'] = Review.query.filter_by(service_id=id).count()
    return jsonify(result), 200


@service_bp.route('/<int:id>', methods=['PUT'])
@require_admin
def update_service(id):
    """PUT /api/services/{id} — 管理员修改服务"""
    service = MedicalService.query.get(id)
    if not service:
        return jsonify({"error": "服务不存在"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    if 'name' in data:
        new_name = data['name'].strip()
        if not new_name:
            return jsonify({"error": "服务名称不能为空"}), 400
        service.name = new_name
    if 'category' in data:
        service.category = data['category'].strip() or None
    if 'description' in data:
        service.description = data['description'].strip() or None
    if 'price' in data:
        service.price = data['price']
    if 'active' in data:
        service.active = bool(data['active'])

    db.session.commit()
    return jsonify({"message": "服务修改成功", "data": service.to_dict()}), 200


@service_bp.route('/<int:id>', methods=['DELETE'])
@require_admin
def delete_service(id):
    """DELETE /api/services/{id} — 管理员删除服务"""
    service = MedicalService.query.get(id)
    if not service:
        return jsonify({"error": "服务不存在"}), 404

    db.session.delete(service)
    db.session.commit()
    return jsonify({"message": "服务已删除"}), 200
