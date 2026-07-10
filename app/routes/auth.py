"""Auth routes — register + login."""
import re
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
    if phone is not None:
        phone = str(phone).strip()
        if phone and not re.match(r'^1[3-9]\d{9}$', phone):
            return jsonify({"error": "手机号必须为11位中国大陆手机号"}), 400

    if not username or not password:
        return jsonify({"error": "用户名和密码不能为空"}), 400

    if AppUser.query.filter_by(username=username).first():
        return jsonify({"error": "用户名已存在"}), 400

    try:
        role = UserRole(role_str)
    except ValueError:
        role = UserRole.USER

    age = data.get('age')
    if age is not None:
        try:
            age = int(age)
        except (ValueError, TypeError):
            return jsonify({"error": "年龄必须为整数"}), 400
        if age < 0 or age > 150:
            return jsonify({"error": "年龄必须在 0-150 之间"}), 400

    try:
        user = AppUser(
            username=username, role=role, phone=phone,
            gender=data.get('gender', '').strip() or None,
            age=age,
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

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
