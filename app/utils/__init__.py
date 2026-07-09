"""Auth decorators — from old git service_api.py."""
from functools import wraps
from flask import request, jsonify
from app.models.user import AppUser


def current_user():
    """从请求头获取当前登录用户."""
    user_id = request.headers.get('X-User-Id')
    if not user_id:
        return None
    return AppUser.query.get(int(user_id))


def require_auth(fn):
    """要求登录."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({"error": "未登录，请先登录"}), 401
        return fn(*args, **kwargs)
    return wrapper


def require_admin(fn):
    """要求管理员权限."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            return jsonify({"error": "未登录，请先登录"}), 401
        if user.role.value != 'ADMIN':
            return jsonify({"error": "仅管理员可执行此操作"}), 403
        return fn(*args, **kwargs)
    return wrapper
