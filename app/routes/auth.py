"""Auth routes — register + login."""
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import AppUser
from app.models.enums import UserRole

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """POST /api/auth/register."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()
    role_str = data.get('role', 'USER')
    phone = data.get('phone')

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    if AppUser.query.filter_by(username=username).first():
        return jsonify({"error": "用户名已存在"}), 400

    try:
        role = UserRole(role_str)
    except ValueError:
        role = UserRole.USER

    user = AppUser(
        username=username, role=role, phone=phone,
        gender=data.get('gender', '').strip() or None,
        age=data.get('age'),
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "注册成功", "data": user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """POST /api/auth/login."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    username = (data.get('username') or '').strip()
    password = (data.get('password') or '').strip()

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    user = AppUser.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "用户不存在"}), 400

    if not user.check_password(password):
        return jsonify({"error": "密码错误"}), 400

    return jsonify({"message": "登录成功", "data": user.to_dict()}), 200
