from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.measurement import DeviceMeasurement
from app.models.employee import Employee
from app.models.device import Device
from datetime import datetime
import uuid
import re

# 기존 블루프린트에 추가하거나 새 블루프린트 생성
# 예: route_mobile/measurement.py 또는 route/measurement.py 파일에 추가
measurement_bp = Blueprint('measurement', __name__)

@measurement_bp.route('/device/measurement', methods=['POST'])
@jwt_required()  # JWT 인증 필요
def add_measurement():
    """
    디바이스로부터 측정 데이터를 받아 데이터베이스에 저장합니다.
    
    요청 본문(JSON):
    {
        "emp_id": "1234567890",
        "device_id": "DEV1234567",
        "battery": 85,
        "hr": 78,
        "temp": 36.5,
        "resp": 16,
        "spo2": 98,
        "acc_x": 0.1,
        "acc_y": 0.2,
        "acc_z": 9.8,
        "gyro_x": 0.01,
        "gyro_y": 0.02,
        "gyro_z": 0.03,
        "heat_risk": 0.2,
        "fall_risk": 0.1
    }
    
    응답:
    {
        "status": "success",
        "message": "측정 데이터가 성공적으로 저장되었습니다.",
        "measurement_id": "M123456789"
    }
    """
    current_app.logger.info("측정 데이터 저장 요청 시작")
    
    # 요청 데이터 가져오기
    data = request.get_json()
    if not data:
        current_app.logger.warning("요청 본문에 JSON 데이터가 없음")
        return jsonify({"status": "error", "message": "JSON 데이터가 필요합니다."}), 400
    
    # 필수 필드 검증
    required_fields = ["emp_id", "device_id", "hr", "temp"]
    for field in required_fields:
        if field not in data:
            current_app.logger.warning(f"필수 필드 누락: {field}")
            return jsonify({
                "status": "error", 
                "message": f"필수 필드 '{field}'가 누락되었습니다."
            }), 400
    
    # 직원 ID 및 기기 ID 존재 여부 확인
    emp_id = data["emp_id"]
    device_id = data["device_id"]
    
    employee = Employee.query.get(emp_id)
    if not employee:
        current_app.logger.warning(f"존재하지 않는 직원 ID: {emp_id}")
        return jsonify({
            "status": "error", 
            "message": "존재하지 않는 직원 ID입니다."
        }), 404
    
    device = Device.query.get(device_id)
    if not device:
        current_app.logger.warning(f"존재하지 않는 기기 ID: {device_id}")
        return jsonify({
            "status": "error", 
            "message": "존재하지 않는 기기 ID입니다."
        }), 404
    
    # 측정 ID 생성 (10자리 고유 ID)
    measurement_id = 'M' + re.sub(r'[^0-9]', '', str(uuid.uuid4()))[:9]
    
    try:
        # 현재 시간 가져오기
        measure_time = datetime.now()
        
        # 새 측정 데이터 생성
        new_measurement = DeviceMeasurement(
            measurement_id=measurement_id,
            emp_id=emp_id,
            device_id=device_id,
            measure_time=measure_time,
            battery=data.get("battery"),
            hr=data.get("hr"),
            temp=data.get("temp"),
            resp=data.get("resp"),
            spo2=data.get("spo2"),
            acc_x=data.get("acc_x"),
            acc_y=data.get("acc_y"),
            acc_z=data.get("acc_z"),
            gyro_x=data.get("gyro_x"),
            gyro_y=data.get("gyro_y"),
            gyro_z=data.get("gyro_z"),
            heat_risk=data.get("heat_risk"),
            fall_risk=data.get("fall_risk")
        )
        
        # 데이터베이스에 저장
        db.session.add(new_measurement)
        db.session.commit()
        
        current_app.logger.info(f"측정 데이터 저장 성공: {measurement_id}")
        
        # 응답 반환
        return jsonify({
            "status": "success",
            "message": "측정 데이터가 성공적으로 저장되었습니다.",
            "measurement_id": measurement_id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"측정 데이터 저장 중 오류 발생: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "측정 데이터 저장 중 오류가 발생했습니다."
        }), 500