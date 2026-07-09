from flask import Blueprint, request, jsonify
from init import db
from datetime import datetime
from sqlalchemy import and_
from appointment import Appointment
from service import Service

appointment_bp = Blueprint('appointment', __name__)

def _current_user():
    """
    临时占位：模拟从 JWT 中获取当前登录用户。
    """
    return getattr(request, 'current_user', None)

def _require_auth(fn):
    """要求登录的装饰器。"""
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


# ============================================================
# 接口1: 创建预约（含冲突检测）
# ============================================================
@appointment_bp.route('/appointments', methods=['POST'])
@_require_auth
def create_appointment():
    """用户创建预约"""
    user = _current_user()
    
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400

    service_name = data.get('service_name', '').strip()
    start_time_str = data.get('start_time')
    end_time_str = data.get('end_time')

    if not all([service_name, start_time_str, end_time_str]):
        return jsonify({"error": "缺少必填参数"}), 400

    # 检查服务是否存在
    service = Service.query.get(service_name)
    if not service:
        return jsonify({"error": "服务不存在"}), 404
    
    if service.state != 'active':
        return jsonify({"error": "该服务当前不可用"}), 400

    try:
        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)
    except ValueError:
        return jsonify({"error": "时间格式错误"}), 400

    if start_time >= end_time:
        return jsonify({"error": "开始时间必须早于结束时间"}), 400

    if start_time < datetime.now():
        return jsonify({"error": "不能预约过去的时间"}), 400

    # 冲突检测
    conflict = Appointment.query.filter(
        and_(
            Appointment.service_name == service_name,
            Appointment.status.in_(['pending', 'confirmed']),
            Appointment.start_time < end_time,
            Appointment.end_time > start_time
        )
    ).first()

    if conflict:
        return jsonify({
            "error": "该时段已被预约",
            "conflict_id": conflict.id,
            "conflict_time": f"{conflict.start_time} ~ {conflict.end_time}"
        }), 409

    appointment = Appointment(
        user_id=user.id,
        service_name=service_name,
        start_time=start_time,
        end_time=end_time,
        status='pending'
    )

    db.session.add(appointment)
    db.session.commit()

    return jsonify({"message": "预约创建成功", "data": appointment.to_dict()}), 201


# ============================================================
# 接口2: 我的预约列表
# ============================================================
@appointment_bp.route('/appointments', methods=['GET'])
@_require_auth
def get_appointments():
    """获取当前用户的预约列表"""
    user = _current_user()
    
    status = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)

    query = Appointment.query.filter_by(user_id=user.id)

    if status:
        valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        if status not in valid_statuses:
            return jsonify({"error": "无效的状态参数"}), 400
        query = query.filter_by(status=status)

    query = query.order_by(Appointment.start_time.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    appointments = pagination.items

    return jsonify({
        "total": pagination.total,
        "page": pagination.page,
        "per_page": pagination.per_page,
        "pages": pagination.pages,
        "data": [a.to_dict() for a in appointments]
    }), 200


# ============================================================
# 接口3: 预约详情
# ============================================================
@appointment_bp.route('/appointments/<int:id>', methods=['GET'])
@_require_auth
def get_appointment(id):
    """获取预约详情"""
    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"error": "预约不存在"}), 404
    
    # 只有本人或管理员可以查看
    user = _current_user()
    if appointment.user_id != user.id and getattr(user, 'role', None) != 'admin':
        return jsonify({"error": "无权查看此预约"}), 403
        
    return jsonify(appointment.to_dict()), 200


# ============================================================
# 接口4: 取消预约
# ============================================================
@appointment_bp.route('/appointments/<int:id>/cancel', methods=['PUT'])
@_require_auth
def cancel_appointment(id):
    """取消预约"""
    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"error": "预约不存在"}), 404

    # 只有本人或管理员可以取消
    user = _current_user()
    if appointment.user_id != user.id and getattr(user, 'role', None) != 'admin':
        return jsonify({"error": "无权取消此预约"}), 403

    if appointment.status == 'cancelled':
        return jsonify({"error": "该预约已取消"}), 400

    if appointment.status == 'completed':
        return jsonify({"error": "已完成的服务无法取消"}), 400

    if appointment.status not in ['pending', 'confirmed']:
        return jsonify({"error": f"当前状态 {appointment.status} 无法取消"}), 400

    appointment.status = 'cancelled'
    db.session.commit()

    return jsonify({"message": "预约已取消", "data": appointment.to_dict()}), 200


# ============================================================
# 接口5: 确认预约（管理员）
# ============================================================
@appointment_bp.route('/appointments/<int:id>/confirm', methods=['PUT'])
@_require_admin
def confirm_appointment(id):
    """管理员确认预约"""
    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"error": "预约不存在"}), 404

    if appointment.status != 'pending':
        return jsonify({"error": f"当前状态 {appointment.status} 无法确认"}), 400

    appointment.status = 'confirmed'
    db.session.commit()

    return jsonify({"message": "预约已确认", "data": appointment.to_dict()}), 200


# ============================================================
# 接口6: 完成预约（管理员）
# ============================================================
@appointment_bp.route('/appointments/<int:id>/complete', methods=['PUT'])
@_require_admin
def complete_appointment(id):
    """管理员完成预约"""
    appointment = Appointment.query.get(id)
    if not appointment:
        return jsonify({"error": "预约不存在"}), 404

    if appointment.status != 'confirmed':
        return jsonify({"error": f"当前状态 {appointment.status} 无法完成"}), 400

    appointment.status = 'completed'
    db.session.commit()

    return jsonify({"message": "预约已完成", "data": appointment.to_dict()}), 200


# ============================================================
# 接口7: 可预约时段
# ============================================================
@appointment_bp.route('/appointments/slots', methods=['GET'])
def get_available_slots():
    """查询某个服务在某天的可预约时段"""
    service_name = request.args.get('service_name', '').strip()
    date_str = request.args.get('date')

    if not service_name or not date_str:
        return jsonify({"error": "缺少必填参数: service_name 和 date"}), 400

    # 检查服务是否存在且可用
    service = Service.query.get(service_name)
    if not service:
        return jsonify({"error": "服务不存在"}), 404
    if service.state != 'active':
        return jsonify({"error": "该服务当前不可用"}), 400

    try:
        start_date = datetime.fromisoformat(f"{date_str}T00:00:00")
        end_date = datetime.fromisoformat(f"{date_str}T23:59:59")
    except ValueError:
        return jsonify({"error": "日期格式错误，请使用 YYYY-MM-DD"}), 400

    # 查询该服务已被预约的时段
    booked = Appointment.query.filter(
        and_(
            Appointment.service_name == service_name,
            Appointment.start_time >= start_date,
            Appointment.end_time <= end_date,
            Appointment.status.in_(['pending', 'confirmed'])
        )
    ).order_by(Appointment.start_time).all()

    booked_slots = []
    for b in booked:
        booked_slots.append({
            'start': b.start_time.hour + b.start_time.minute / 60,
            'end': b.end_time.hour + b.end_time.minute / 60
        })

    # 生成全天时段（9:00-18:00，每小时一个时段）
    all_slots = []
    current_hour = 9.0

    while current_hour + 1 <= 18.0:
        start_hour = int(current_hour)
        start_min = int((current_hour - start_hour) * 60)
        end_hour = int(current_hour + 1)
        end_min = int((current_hour + 1 - end_hour) * 60)

        is_booked = False
        for booked_slot in booked_slots:
            if not (current_hour + 1 <= booked_slot['start'] or
                   current_hour >= booked_slot['end']):
                is_booked = True
                break

        all_slots.append({
            'start': f"{date_str}T{start_hour:02d}:{start_min:02d}:00",
            'end': f"{date_str}T{end_hour:02d}:{end_min:02d}:00",
            'available': not is_booked
        })

        current_hour += 1

    return jsonify({
        'date': date_str,
        'service_name': service_name,
        'slots': all_slots
    }), 200


# ============================================================
# 接口8: 批量取消（管理员）
# ============================================================
@appointment_bp.route('/appointments/batch-cancel', methods=['POST'])
@_require_admin
def batch_cancel():
    """管理员批量取消预约"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "请求体不能为空"}), 400
        
    ids = data.get('ids', [])

    if not ids or not isinstance(ids, list):
        return jsonify({"error": "请提供有效的ID列表"}), 400

    if len(ids) > 100:
        return jsonify({"error": "一次最多取消100个预约"}), 400

    cancelled = []
    failed = []

    for aid in ids:
        appointment = Appointment.query.get(aid)
        if not appointment:
            failed.append({'id': aid, 'reason': '预约不存在'})
            continue

        if appointment.status in ['cancelled', 'completed']:
            failed.append({'id': aid, 'reason': f'当前状态 {appointment.status} 无法取消'})
            continue

        appointment.status = 'cancelled'
        cancelled.append(aid)

    db.session.commit()

    return jsonify({
        'message': f'成功取消 {len(cancelled)} 个预约',
        'cancelled': cancelled,
        'failed': failed
    }), 200
