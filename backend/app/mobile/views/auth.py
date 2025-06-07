# app/mobile/views/auth.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from ..service.auth_service import AuthService
from app.schema import LoginSchema
from datetime import datetime, time, timedelta
from app.model import DeviceManagement, Device, db, Employee
import random

from datetime import datetime
from zoneinfo import ZoneInfo

kst_now = datetime.now(ZoneInfo("Asia/Seoul"))

# 모바일 인증 관련 Blueprint 생성
mobile_auth_bp = Blueprint('mobile_auth', __name__)

@mobile_auth_bp.route('/login', methods=['POST'])
def mobile_login():
    """
    모바일 로그인 처리
    - 본인 출근 기록 생성 (중복 방지)
    - EN0003이 로그인할 경우, 오늘 첫 출근일 때만 79명 더미 출근 생성
    """
    try:
        schema = LoginSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "유효하지 않은 입력입니다", "details": err.messages}), 400

    emp_id = data['id']
    password = data['password']

    access_token, error = AuthService.login(emp_id, password)
    if error:
        return jsonify({"error": error}), 401

    user_data, profile_error = AuthService.get_user_profile(emp_id)
    if profile_error:
        return jsonify({"error": profile_error}), 404

    try:
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        today = now.date()

        # ✅ EN0003 더미 출근 생성 여부 미리 판단
        create_dummy = False
        if emp_id == 'EN0003':
            en_record_exists = DeviceManagement.query.filter_by(emp_id='EN0003')\
                .filter(db.func.date(DeviceManagement.check_in) == today).first()
            if not en_record_exists:
                create_dummy = True

        # ✅ 본인 출근 기록 생성 (중복 방지)
        device = Device.query.filter_by(emp_id=emp_id).first()
        if device:
            existing = DeviceManagement.query.filter_by(emp_id=emp_id, device_id=device.device_id)\
                .filter(db.func.date(DeviceManagement.check_in) == today)\
                .filter(DeviceManagement.check_out == None).first()

            if not existing:
                base_time = datetime.combine(today, time(6, 30), tzinfo=ZoneInfo("Asia/Seoul"))
                check_in_time = base_time + timedelta(seconds=random.randint(0, 40 * 60))

                db.session.add(DeviceManagement(
                    emp_id=emp_id,
                    device_id=device.device_id,
                    check_in=check_in_time
                ))
                db.session.commit()
                print(f"[본인 출근] {emp_id}, {device.device_id}, {check_in_time}")
            else:
                print(f"[본인 출근 생략] 이미 출근함: {emp_id}")
        else:
            print(f"[경고] 디바이스 없음: {emp_id}")

        # ✅ EN0003이 오늘 첫 출근일 경우에만 더미 출근 생성
        if create_dummy:
            others = Employee.query.filter(Employee.emp_id != emp_id).all()
            random.shuffle(others)

            dummy_created = 0
            for e in others[:79]:
                d = Device.query.filter_by(emp_id=e.emp_id).first()
                if not d:
                    continue

                exists = DeviceManagement.query.filter_by(emp_id=e.emp_id, device_id=d.device_id)\
                    .filter(db.func.date(DeviceManagement.check_in) == today).first()

                if not exists:
                    dummy_time = datetime.combine(today, time(6, 30), tzinfo=ZoneInfo("Asia/Seoul")) + \
                                 timedelta(seconds=random.randint(0, 40 * 60))
                    db.session.add(DeviceManagement(
                        emp_id=e.emp_id,
                        device_id=d.device_id,
                        check_in=dummy_time
                    ))
                    dummy_created += 1

            db.session.commit()
            print(f"[더미 출근 생성] {dummy_created}명 생성 완료 (요청자: EN0003)")

    except Exception as e:
        db.session.rollback()
        print(f"[에러] 출근 처리 실패: {str(e)}")

    return jsonify({
        "message": "로그인 성공",
        "token": access_token,
        "user": user_data
    }), 200
    

@mobile_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def mobile_logout():
    """
    모바일 로그아웃 처리
    - JWT 토큰 블랙리스트 등록
    - 본인 퇴근 기록 처리
    - EN0003이 로그아웃할 경우, 오늘 출근한 직원 중 본인을 제외한 79명을 무작위로 골라 퇴근 처리
    """
    jwt_payload = get_jwt()
    emp_id = get_jwt_identity()

    success = AuthService.logout(jwt_payload)

    if success:
        try:
            now = datetime.now(ZoneInfo("Asia/Seoul"))
            today = now.date()

            # ✅ 1. 본인 퇴근 처리
            device = Device.query.filter_by(emp_id=emp_id).first()
            if device:
                latest = DeviceManagement.query.filter_by(
                    emp_id=emp_id,
                    device_id=device.device_id,
                    check_out=None
                ).order_by(DeviceManagement.check_in.desc()).first()

                if latest:
                    latest.check_out = now
                    db.session.commit()
                    print(f"[본인 퇴근] {emp_id}, {device.device_id}, {now}")
                else:
                    print(f"[본인 퇴근 없음] {emp_id}: check_out=None 기록 없음")

            # ✅ 2. EN0003일 경우에만 더미 직원 퇴근 처리
            if emp_id == 'EN0003':
                # (1) 오늘 출근한 직원 중 본인 제외
                emp_ids_today = db.session.query(DeviceManagement.emp_id)\
                    .filter(db.func.date(DeviceManagement.check_in) == today)\
                    .filter(DeviceManagement.emp_id != emp_id)\
                    .distinct().all()

                emp_ids_today = [e[0] for e in emp_ids_today]
                random.shuffle(emp_ids_today)

                dummy_updated = 0
                for emp_dummy in emp_ids_today[:79]:
                    device = Device.query.filter_by(emp_id=emp_dummy).first()
                    if not device:
                        continue

                    record = DeviceManagement.query.filter_by(emp_id=emp_dummy, device_id=device.device_id)\
                        .filter(db.func.date(DeviceManagement.check_in) == today).first()

                    if record:
                        # 퇴근 시간: 17:45~18:15 사이 랜덤
                        rand_checkout = datetime.combine(today, time(17, 45), tzinfo=ZoneInfo("Asia/Seoul")) + \
                                        timedelta(seconds=random.randint(0, 30 * 60))

                        if not record.check_out or rand_checkout > record.check_out:
                            record.check_out = rand_checkout
                            dummy_updated += 1

                db.session.commit()
                print(f"[더미 퇴근] {dummy_updated}명 퇴근 처리 완료 (요청자: EN0003)")

        except Exception as e:
            db.session.rollback()
            print(f"[에러] 퇴근 처리 실패: {str(e)}")

    if not success:
        return jsonify({"error": "로그아웃 처리 중 오류 발생"}), 500

    return jsonify({"message": "로그아웃 성공"}), 200