

from flask import Blueprint, request, jsonify
from init import db
from service import Service
from review import Review
from complaint import Complaint

service_bp = Blueprint('service', __name__)

def _current_user():
    """
    临时占位：模拟从 JWT 中获取当前登录用户。
    """
    # TODO: 替换为 request.current_user
    return getattr(request, 'current_user', None)

def _require_auth(fn):
    """临时占位：要求登录的装饰器。"""
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = _current_user()
        if not user:
            return jsonify({"error": "未登录，请先登录"}), 401
        return fn(*args, **kwargs)
    return wrapper

def _require_admin(fn):
    """要求管理员。"""
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = _current_user()
        if not user:
            return jsonify({"error": "未登录，请先登录"}), 401
        if getattr(user, 'role', None) != 'admin':
            return jsonify({"error": "仅管理员可执行此操作"}), 403
        return fn(*args, **kwargs)
    return wrapper

@service_bp.route('/services', methods=['GET'])
def get_services():
    
    q = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    query = Service.query.filter(Service.state == 'active')

    if q:
        like_pattern = f'%{q}%'
        query = query.filter(
            db.or_(Service.name.like(like_pattern), Service.description.like(like_pattern))
        )

    query = query.order_by(Service.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    services = pagination.items

    return jsonify({
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "data": [s.to_dict() for s in services]
    }), 200


@service_bp.route('/services', methods=['POST'])
@_require_admin
def create_service():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    name = data.get('name', '').strip()
    if not name:
        return jsonify({"error": "科室名称不能为空"}), 400

    service = Service(
        name=name,
        description=data.get('description', '').strip(),
        price=data.get('price', 0)
    )

    db.session.add(service)
    db.session.commit()

    return jsonify({"message": "服务发布成功", "data": service.to_dict()}), 201


@service_bp.route('/services/<string:name>', methods=['GET'])
def get_service(name):
    service = Service.query.get(name)
    if not service:
        return jsonify({"error": "服务不存在"}), 404
    result = service.to_dict()

    # 评论总数
    review_count = Review.query.count()
    result['review_count'] = review_count

    return jsonify(result), 200


@service_bp.route('/services/<string:name>', methods=['PUT'])
@_require_admin
def update_service(name):
    service = Service.query.get(name)
    if not service:
        return jsonify({"error": "服务不存在"}), 404

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    if 'name' in data:
        new_name = data['name'].strip()
        if not new_name:
            return jsonify({"error": "科室名称不能为空"}), 400
        service.name = new_name

    if 'description' in data:
        service.description = data['description'].strip()

    if 'price' in data:
        service.price = data['price']

    if 'state' in data:
        if data['state'] not in ('active', 'inactive'):
            return jsonify({"error": "状态只能为 active 或 inactive"}), 400
        service.state = data['state']

    db.session.commit()

    return jsonify({"message": "服务修改成功", "data": service.to_dict()}), 200


@service_bp.route('/services/<string:name>', methods=['DELETE'])
@_require_admin
def delete_service(name):
    """管理员删除服务"""
    service = Service.query.get(name)
    if not service:
        return jsonify({"error": "服务不存在"}), 404

    db.session.delete(service)
    db.session.commit()

    return jsonify({"message": "服务已删除"}), 200

@service_bp.route('/reviews', methods=['POST'])
@_require_auth
def create_review():
    """登录用户发表评论"""
    user = _current_user()

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    comment = data.get('comment', '').strip()
    if not comment:
        return jsonify({"error": "评论内容不能为空"}), 400

    review = Review(
        user_id=user.id,
        comment=comment
    )

    db.session.add(review)
    db.session.commit()

    return jsonify({"message": "评论发表成功", "data": review.to_dict()}), 201


@service_bp.route('/reviews', methods=['GET'])
def get_reviews():
    """获取评论区列表（公开，所有人可见）"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    query = Review.query.order_by(Review.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "data": [r.to_dict() for r in pagination.items]
    }), 200

@service_bp.route('/complaints', methods=['POST'])
@_require_auth
def create_complaint():
    """登录用户提交投诉/反馈"""
    user = _current_user()
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400
    service_name = data.get('service_name', '').strip()
    if not service_name:
        return jsonify({"error": "请指定服务名称"}), 400
    service = Service.query.get(service_name)
    if not service:
        return jsonify({"error": "服务不存在"}), 404
    content = data.get('content', '').strip()
    if not content:
        return jsonify({"error": "反馈内容不能为空"}), 400
    existing = Complaint.query.filter_by(user_id=user.id, service_name=service_name).first()
    if existing:
        return jsonify({"error": "你已经对该服务提交过反馈，不能重复提交"}), 409
    complaint = Complaint(
        user_id=user.id,
        service_name=service_name,
        content=content
    )
    db.session.add(complaint)
    db.session.commit()
    return jsonify({"message": "反馈提交成功", "data": complaint.to_dict()}), 201
