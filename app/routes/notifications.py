"""Notification routes — mirrors NotificationController.java + NotificationService.java."""
from flask import Blueprint, jsonify
from app.models.notification import Notification

notification_bp = Blueprint('notifications', __name__)


@notification_bp.route('/user/<int:user_id>', methods=['GET'])
def list_by_user(user_id):
    """GET /api/notifications/user/{userId}."""
    notifications = Notification.query.filter_by(user_id=user_id).order_by(
        Notification.created_at.desc()
    ).all()
    return jsonify({"data": [n.to_dict() for n in notifications]}), 200
