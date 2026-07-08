from flask import Blueprint, request, jsonify
from models import db, Appointment
from datetime import datetime
from sqlalchemy import and_

appointment_bp = Blueprint('appointment', __name__, url_prefix='/api/appointments')


# ============================================================
# 接口1: 创建预约（含冲突检测）
# ============================================================
@appointment_bp.route('', methods=['POST'])
def create_appointment():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求体不能为空'}), 400

        user_id = data.get('user_id')
        service_id = data.get('service_id')
        provider_id = data.get('provider_id')
        start_time_str = data.get('start_time')
        end_time_str = data.get('end_time')

        if not all([user_id, service_id, provider_id, start_time_str, end_time_str]):
            return jsonify({'error': '缺少必填参数'}), 400

        start_time = datetime.fromisoformat(start_time_str)
        end_time = datetime.fromisoformat(end_time_str)

        if start_time >= end_time:
            return jsonify({'error': '开始时间必须早于结束时间'}), 400

        if start_time < datetime.now():
            return jsonify({'error': '不能预约过去的时间'}), 400

        # 冲突检测
        conflict = Appointment.query.filter(
            and_(
                Appointment.provider_id == provider_id,
                Appointment.status.in_(['pending', 'confirmed']),
                Appointment.start_time < end_time,
                Appointment.end_time > start_time
            )
        ).first()

        if conflict:
            return jsonify({
                'error': '该时段已被预约',
                'conflict_id': conflict.id,
                'conflict_time': f"{conflict.start_time} ~ {conflict.end_time}"
            }), 409

        appointment = Appointment(
            user_id=user_id,
            service_id=service_id,
            provider_id=provider_id,
            start_time=start_time,
            end_time=end_time,
            status='pending'
        )

        db.session.add(appointment)
        db.session.commit()

        return jsonify({
            'message': '预约创建成功',
            'data': appointment.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': f'时间格式错误: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================
# 接口2: 我的预约列表
# ============================================================
@appointment_bp.route('', methods=['GET'])
def get_appointments():
    try:
        user_id = request.args.get('user_id', type=int)
        status = request.args.get('status')

        query = Appointment.query

        if user_id:
            query = query.filter_by(user_id=user_id)
        if status:
            valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
            if status not in valid_statuses:
                return jsonify({'error': '无效的状态参数'}), 400
            query = query.filter_by(status=status)

        query = query.order_by(Appointment.created_at.desc())

        appointments = query.all()

        return jsonify([a.to_dict() for a in appointments])

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# 接口3: 预约详情
# ============================================================
@appointment_bp.route('/<int:id>', methods=['GET'])
def get_appointment(id):
    try:
        appointment = Appointment.query.get(id)
        if not appointment:
            return jsonify({'error': '预约不存在'}), 404
        return jsonify(appointment.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# 接口4: 取消预约
# ============================================================
@appointment_bp.route('/<int:id>/cancel', methods=['PUT'])
def cancel_appointment(id):
    try:
        appointment = Appointment.query.get(id)
        if not appointment:
            return jsonify({'error': '预约不存在'}), 404

        if appointment.status == 'cancelled':
            return jsonify({'error': '该预约已取消'}), 400

        if appointment.status == 'completed':
            return jsonify({'error': '已完成的服务无法取消'}), 400

        if appointment.status not in ['pending', 'confirmed']:
            return jsonify({'error': f'当前状态 {appointment.status} 无法取消'}), 400

        appointment.status = 'cancelled'
        db.session.commit()

        return jsonify({
            'message': '预约已取消',
            'data': appointment.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================
# 接口5: 确认预约
# ============================================================
@appointment_bp.route('/<int:id>/confirm', methods=['PUT'])
def confirm_appointment(id):
    try:
        appointment = Appointment.query.get(id)
        if not appointment:
            return jsonify({'error': '预约不存在'}), 404

        if appointment.status != 'pending':
            return jsonify({'error': f'当前状态 {appointment.status} 无法确认'}), 400

        appointment.status = 'confirmed'
        db.session.commit()

        return jsonify({
            'message': '预约已确认',
            'data': appointment.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================
# 接口6: 完成预约
# ============================================================
@appointment_bp.route('/<int:id>/complete', methods=['PUT'])
def complete_appointment(id):
    try:
        appointment = Appointment.query.get(id)
        if not appointment:
            return jsonify({'error': '预约不存在'}), 404

        if appointment.status != 'confirmed':
            return jsonify({'error': f'当前状态 {appointment.status} 无法完成'}), 400

        appointment.status = 'completed'
        db.session.commit()

        return jsonify({
            'message': '预约已完成',
            'data': appointment.to_dict()
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================
# 接口7: 可预约时段
# ============================================================
@appointment_bp.route('/slots', methods=['GET'])
def get_available_slots():
    try:
        provider_id = request.args.get('provider_id', type=int)
        date_str = request.args.get('date')

        if not provider_id or not date_str:
            return jsonify({'error': '缺少必填参数: provider_id 和 date'}), 400

        try:
            start_date = datetime.fromisoformat(f"{date_str}T00:00:00")
            end_date = datetime.fromisoformat(f"{date_str}T23:59:59")
        except ValueError:
            return jsonify({'error': '日期格式错误，请使用 YYYY-MM-DD'}), 400

        booked = Appointment.query.filter(
            and_(
                Appointment.provider_id == provider_id,
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
            'provider_id': provider_id,
            'slots': all_slots
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================
# 接口8: 批量取消
# ============================================================
@appointment_bp.route('/batch-cancel', methods=['POST'])
def batch_cancel():
    try:
        data = request.get_json()
        ids = data.get('ids', [])

        if not ids or not isinstance(ids, list):
            return jsonify({'error': '请提供有效的ID列表'}), 400

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
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500