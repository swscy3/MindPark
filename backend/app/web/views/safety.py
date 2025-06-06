# app/web/safety.py
from flask import Blueprint, jsonify, Response
from flask_jwt_extended import jwt_required
from datetime import datetime
import time
import json
import traceback
import os

# Flask 앱 인스턴스와 DB 세션을 명시적으로 가져오기
from app import create_app, db
from app.model import (
    HealthAnomaly, Employee, EmergencyContact, 
    DeviceMeasurement, Device
)

safety_bp = Blueprint('safety', __name__)

def convert_picture_to_url(picture_path):
    """절대 경로를 웹 URL로 변환"""
    if not picture_path:
        return None
    
    filename = os.path.basename(picture_path)
    # 확장자가 없으면 .jpg 추가
    if not os.path.splitext(filename)[1]:
        filename += '.jpg'
    
    return f"/uploads/pictures/{filename}"

def format_employee_data(anomaly, employee, emergency_contact, latest_measurement, device):
    """직원 데이터를 JSON 형태로 포맷팅"""
    
    return {
        "emp_id": employee.emp_id,
        "basic_info": {
            "name": employee.name,
            "age": employee.age,
            "gender": employee.gender,
            "picture": convert_picture_to_url(employee.picture)
        },
        "emergency_contact": {
            "contact_name": emergency_contact.contact_name if emergency_contact else None,
            "relation": emergency_contact.relation if emergency_contact else None,
            "phone": emergency_contact.contact_phone if emergency_contact else None
        },
        "current_vitals": {
            "heart_rate": latest_measurement.hr if latest_measurement else None,
            "spo2": latest_measurement.spo2 if latest_measurement else None,
            "temperature": latest_measurement.temp if latest_measurement else None,
            "steps": latest_measurement.walk if latest_measurement else None,
            "measurement_time": latest_measurement.measure_time.isoformat() if latest_measurement and latest_measurement.measure_time else None
        },
        "device_info": {
            "device_name": device.product if device else None,
            "battery_level": latest_measurement.battery if latest_measurement else None,
            "device_id": device.device_id if device else None
        },
        "location": {
            "latitude": anomaly.loc_x,
            "longitude": anomaly.loc_y,
            "location_time": anomaly.anomaly_time.isoformat() if anomaly.anomaly_time else None
        },
        "risk_info": {
            "risk_level": anomaly.risk,
            "symptom": anomaly.symptom,
            "detected_time": anomaly.anomaly_time.isoformat() if anomaly.anomaly_time else None,
            "status": anomaly.status
        }
    }

def get_employees_by_risk_level_data(risk_level, app_context):
    """위험도별 직원 데이터 조회 (SSE용)"""
    with app_context:
        try:
            # 위험도별 HealthAnomaly 조회
            anomalies = HealthAnomaly.query\
                .filter(HealthAnomaly.risk == risk_level)\
                .filter(HealthAnomaly.status == '처리중')\
                .all()
            
            employees_data = []
            
            for anomaly in anomalies:
                # 직원 기본 정보
                employee = Employee.query.filter_by(emp_id=anomaly.emp_id).first()
                if not employee:
                    continue
                    
                # 응급 연락처
                emergency_contact = EmergencyContact.query.filter_by(emp_id=anomaly.emp_id).first()
                
                # 최신 생체 데이터
                latest_measurement = DeviceMeasurement.query\
                    .filter_by(emp_id=anomaly.emp_id)\
                    .order_by(DeviceMeasurement.measure_time.desc())\
                    .first()
                
                # 디바이스 정보
                device = None
                if latest_measurement:
                    device = Device.query.filter_by(device_id=latest_measurement.device_id).first()
                
                # 데이터 포맷팅
                employee_data = format_employee_data(
                    anomaly, employee, emergency_contact, latest_measurement, device
                )
                employees_data.append(employee_data)
            
            return employees_data
            
        except Exception as e:
            raise e

@safety_bp.route('/danger-employees/stream')
@jwt_required()
def danger_employees_stream():
    """
    위험 직원 실시간 스트림 API
    GET /api/web/safety/danger-employees/stream
    """
    # 앱 인스턴스 생성
    app = create_app()
    
    def generate_danger_stream():
        # 초기 연결 메시지
        yield "data: {\"status\":\"connected\",\"message\":\"위험 직원 데이터 스트림 연결 성공\"}\n\n"
        time.sleep(1)
        
        while True:
            try:
                employees_data = get_employees_by_risk_level_data('위험', app.app_context())
                
                # 응답 데이터 생성
                response_data = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "data": {
                        "employees": employees_data
                    }
                }
                
                # SSE 형식으로 전송
                yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                error_data = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            # 30초 대기 (위험자는 더 자주 체크)
            time.sleep(300)
    
    return Response(
        generate_danger_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Content-Type': 'text/event-stream',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@safety_bp.route('/caution-employees/stream')
@jwt_required()
def caution_employees_stream():
    """
    주의 직원 실시간 스트림 API
    GET /api/web/safety/caution-employees/stream
    """
    # 앱 인스턴스 생성
    app = create_app()
    
    def generate_caution_stream():
        # 초기 연결 메시지
        yield "data: {\"status\":\"connected\",\"message\":\"주의 직원 데이터 스트림 연결 성공\"}\n\n"
        time.sleep(1)
        
        while True:
            try:
                employees_data = get_employees_by_risk_level_data('주의', app.app_context())
                
                # 응답 데이터 생성
                response_data = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "success",
                    "data": {
                        "employees": employees_data
                    }
                }
                
                # SSE 형식으로 전송
                yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                error_data = {
                    "timestamp": datetime.now().isoformat(),
                    "status": "error",
                    "message": str(e),
                    "traceback": traceback.format_exc()
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            # 1분 대기 (주의는 조금 덜 자주)
            time.sleep(300)
    
    return Response(
        generate_caution_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Content-Type': 'text/event-stream',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )
