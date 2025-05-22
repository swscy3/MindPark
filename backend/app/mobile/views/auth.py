# app/mobile/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from marshmallow import ValidationError
from ..service.auth_service import AuthService
from app.schema import LoginSchema  # 공용 스키마 사용
from datetime import datetime
from app.model import DeviceManagement, Device, db, Employee

# 모바일 인증 블루프린트 생성
mobile_auth_bp = Blueprint('mobile_auth', __name__)

@mobile_auth_bp.route('/login', methods=['POST'])
def mobile_login():
    """모바일 로그인 API"""
    try:
        # 1. 입력 데이터 검증
        schema = LoginSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            "error": "유효하지 않은 입력입니다",
            "details": err.messages
        }), 400
    
    emp_id = data['id']
    password = data['password']
    
    # 2. 서비스 레이어 호출
    access_token, error = AuthService.login(emp_id, password)
    
    if error:
        return jsonify({"error": error}), 401
    
    # 3. 사용자 정보 조회
    user_data, profile_error = AuthService.get_user_profile(emp_id)
    
    if profile_error:
        return jsonify({"error": profile_error}), 404
    
    # 4. 출근 기록 추가
    try:
        # Device 테이블에서 emp_id로 디바이스 조회
        device = Device.query.filter_by(emp_id=emp_id).first()
        
        if device:
            device_id = device.device_id
            now = datetime.now()
            
            # 출근 기록 생성
            check_in_record = DeviceManagement(
                device_id=device_id,
                emp_id=emp_id,
                check_in=now
            )
            
            # DB에 저장
            db.session.add(check_in_record)
            db.session.commit()
            print(f"출근 기록 생성: 직원 {emp_id}, 디바이스 {device_id}, 시간 {now}")
        else:
            print(f"출근 기록 생성 실패: 직원 {emp_id}에 연결된 디바이스를 찾을 수 없습니다")
    except Exception as e:
        print(f"출근 기록 생성 실패: {str(e)}")
        # 출근 기록 실패해도 로그인은 허용
        
    # 5. 응답 반환
    return jsonify({
        "message": "로그인 성공",
        "token": access_token,
        "user": user_data
    }), 200
    
    
@mobile_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def mobile_logout():
    """모바일 로그아웃 API"""
    # JWT 페이로드와 emp_id 가져오기
    jwt_payload = get_jwt()
    emp_id = get_jwt_identity()
    
    # 데이터베이스 기반 토큰 블랙리스트에 추가
    success = AuthService.logout(jwt_payload)
    
    if success:
        # 퇴근 기록 업데이트
        try:
            now = datetime.now()
            
            # Device 테이블에서 emp_id로 디바이스 조회
            device = Device.query.filter_by(emp_id=emp_id).first()
            
            if device:
                device_id = device.device_id
                
                # 해당 직원의 해당 디바이스 출근 기록 중 퇴근 시간이 없는 가장 최근 기록 찾기
                latest_check_in = DeviceManagement.query.filter_by(
                    emp_id=emp_id,
                    device_id=device_id, 
                    check_out=None
                ).order_by(DeviceManagement.check_in.desc()).first()
                
                if latest_check_in:
                    latest_check_in.check_out = now
                    db.session.commit()
                    print(f"퇴근 기록 업데이트: 직원 {emp_id}, 디바이스 {device_id}, 시간 {now}")
                else:
                    print(f"퇴근 기록 업데이트 실패: 디바이스 {device_id}의 출근 기록 없음 (직원 {emp_id})")
            else:
                # 직원에 연결된 디바이스를 찾을 수 없는 경우, 가장 최근 출근 기록 업데이트
                print(f"직원 {emp_id}에 연결된 디바이스를 찾을 수 없어 가장 최근 출근 기록을 업데이트합니다.")
                latest_check_in = DeviceManagement.query.filter_by(
                    emp_id=emp_id, 
                    check_out=None
                ).order_by(DeviceManagement.check_in.desc()).first()
                
                if latest_check_in:
                    latest_check_in.check_out = now
                    db.session.commit()
                    device_id = latest_check_in.device_id
                    print(f"퇴근 기록 업데이트: 직원 {emp_id}, 디바이스 {device_id}, 시간 {now}")
                else:
                    print(f"퇴근 기록 업데이트 실패: 출근 기록 없음 (직원 {emp_id})")
        except Exception as e:
            print(f"퇴근 기록 업데이트 실패: {str(e)}")
    
    if not success:
        return jsonify({"error": "로그아웃 처리 중 오류가 발생했습니다"}), 500
    
    return jsonify({"message": "로그아웃 성공"}), 200