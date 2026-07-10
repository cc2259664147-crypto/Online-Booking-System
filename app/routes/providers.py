"""Provider routes — mirrors ProviderController.java + ProviderService.java."""
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.user import AppUser
from app.models.provider import ProviderProfile
from app.models.enums import UserRole

provider_bp = Blueprint('providers', __name__)


@provider_bp.route('', methods=['POST'])
def register():
    """POST /api/providers — ProviderRegisterRequest."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    user_id = data.get('userId')
    org_name = (data.get('organizationName') or '').strip()

    if not user_id or not org_name:
        return jsonify({"error": "userId和organizationName不能为空"}), 400

    user = AppUser.query.get(user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 400

    # Only upgrade USER to PROVIDER, don't downgrade ADMIN
    if user.role == UserRole.USER:
        user.role = UserRole.PROVIDER
        db.session.flush()

    profile = ProviderProfile(
        user_id=user_id,
        organization_name=org_name,
        address=data.get('address', '').strip() or None,
        description=data.get('description', '').strip() or None,
        approved=True,
    )
    db.session.add(profile)
    db.session.commit()

    return jsonify({"message": "服务提供者注册成功", "data": profile.to_dict()}), 201
