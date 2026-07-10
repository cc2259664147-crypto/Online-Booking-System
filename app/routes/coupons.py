"""Coupon routes — mirrors CouponController.java + CouponService.java."""
from datetime import date
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.coupon import Coupon

coupon_bp = Blueprint('coupons', __name__)


@coupon_bp.route('', methods=['POST'])
def create():
    """POST /api/coupons — CouponRequest."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    code = (data.get('code') or '').strip()
    discount_amount = data.get('discountAmount')
    valid_until_str = data.get('validUntil')

    if not code or discount_amount is None or not valid_until_str:
        return jsonify({"error": "code, discountAmount, validUntil 不能为空"}), 400

    try:
        valid_until = date.fromisoformat(valid_until_str)
    except ValueError:
        return jsonify({"error": "validUntil 格式错误，请使用 YYYY-MM-DD 格式"}), 400

    existing = Coupon.query.filter_by(code=code).first()
    if existing:
        return jsonify({"error": "优惠券代码已存在"}), 400

    coupon = Coupon(
        code=code,
        discount_amount=discount_amount,
        valid_until=valid_until,
        active=True,
    )
    db.session.add(coupon)
    db.session.commit()
    return jsonify({"message": "优惠券创建成功", "data": coupon.to_dict()}), 201


@coupon_bp.route('/<string:code>/validate', methods=['GET'])
def validate(code):
    """GET /api/coupons/{code}/validate."""
    coupon = Coupon.query.filter_by(code=code).first()
    if not coupon:
        return jsonify({"error": "优惠券不存在"}), 404

    if not coupon.active or coupon.valid_until < date.today():
        return jsonify({"error": "优惠券不可用或已过期"}), 400

    return jsonify({"message": "优惠券有效", "data": coupon.to_dict()}), 200


@coupon_bp.route('', methods=['GET'])
def all_coupons():
    """GET /api/coupons — list all coupons."""
    coupons = Coupon.query.order_by(Coupon.id.desc()).all()
    return jsonify({"data": [c.to_dict() for c in coupons]}), 200
