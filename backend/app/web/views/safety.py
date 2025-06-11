# app/web/safety.py
from flask import Blueprint, jsonify, Response, request
from datetime import datetime
import time
import json
import os

# Flask 앱 인스턴스와 DB 세션을 명시적으로 가져오기
from app import create_app, db
from app.model import (
    HealthAnomaly, Employee, EmergencyContact, 
    DeviceMeasurement, Device
)

from app.util.auth import verify_token_from_query
from app.util.time_utils import (  # 🔧 한국시간 유틸리티 추가
    get_korea_now_iso, 
    to_korea_time
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
    """
    직원 데이터를 JSON 형태로 포맷팅 (🔧 한국시간 처리 개선)
    """
    return {
        "emp_id": employee.emp_id,
        "basic_info": {
            "name": employee.name,
            "age": employee.age,
            "gender": employee.gender,
            "department": employee.dept,  # 🔧 부서 정보 추가
            "position": employee.position,  # 🔧 직급 정보 추가
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
            "respiration": latest_measurement.resp if latest_measurement else None,  # 🔧 호흡수 추가
            "steps": latest_measurement.walk if latest_measurement else None,
            "measurement_time": to_korea_time(latest_measurement.measure_time) if latest_measurement and latest_measurement.measure_time else None  # 🔧 한국시간 변환
        },
        "device_info": {
            "device_name": device.product if device else None,
            "battery_level": latest_measurement.battery if latest_measurement else None,
            "device_id": device.device_id if device else None,
            "device_model": device.model if device else None  # 🔧 디바이스 모델 추가
        },
        "location": {
            "latitude": anomaly.loc_x,
            "longitude": anomaly.loc_y,
            "location_time": to_korea_time(anomaly.anomaly_time)  # 🔧 한국시간 변환
        },
        "risk_info": {
            "anomaly_id": anomaly.anomaly_id,  # 🔧 이상 ID 추가
            "risk_level": anomaly.risk,
            "symptom": anomaly.symptom,
            "detected_time": to_korea_time(anomaly.anomaly_time),  # 🔧 한국시간 변환
            "status": anomaly.status,
            "action_content": anomaly.action_content  # 🔧 조치 내용 추가
        }
    }

def get_employees_by_risk_level_data(risk_level, app_context):
    """
    위험도별 직원 데이터 조회 (SSE용) - 🔧 에러 핸들링 강화
    """
    with app_context:
        try:
            # 위험도별 HealthAnomaly 조회
            anomalies = HealthAnomaly.query\
                .filter(HealthAnomaly.risk == risk_level)\
                .filter(HealthAnomaly.status == '처리중')\
                .order_by(HealthAnomaly.anomaly_time.desc())\
                .all()  # 🔧 최신순 정렬 추가
            
            employees_data = []
            
            for anomaly in anomalies:
                try:
                    # 직원 기본 정보
                    employee = Employee.query.filter_by(emp_id=anomaly.emp_id).first()
                    if not employee:
                        print(f"[WARNING] 직원 {anomaly.emp_id}을 찾을 수 없습니다.")
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
                    
                except Exception as emp_error:
                    print(f"[ERROR] 직원 {anomaly.emp_id} 데이터 처리 오류: {str(emp_error)}")
                    continue  # 개별 직원 오류 시 다음 직원 계속 처리
            
            return employees_data
            
        except Exception as e:
            print(f"[ERROR] 위험도 {risk_level} 직원 데이터 조회 오류: {str(e)}")
            raise e

@safety_bp.route('/danger-employees/stream')
def danger_employees_stream():
    """
    위험 직원 실시간 스트림 API
    GET /api/web/safety/danger-employees/stream?token=JWT_TOKEN
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    # 앱 인스턴스 생성
    app = create_app()
    
    def generate_danger_stream():
        # 🔧 한국시간으로 초기 연결 메시지
        initial_message = {
            "status": "connected",
            "message": "위험 직원 데이터 스트림 연결 성공",
            "timestamp": get_korea_now_iso(),
            "risk_level": "위험"
        }
        yield f"data: {json.dumps(initial_message, ensure_ascii=False)}\n\n"
        time.sleep(1)
        
        while True:
            try:
                employees_data = get_employees_by_risk_level_data('위험', app.app_context())
                
                # 응답 데이터 생성
                response_data = {
                    "timestamp": get_korea_now_iso(),  # 🔧 한국시간 사용
                    "status": "success",
                    "data": {
                        "risk_level": "위험",
                        "employees": employees_data,
                        "total_count": len(employees_data)  # 🔧 총 인원수 추가
                    },
                    "meta": {
                        "timezone": "Asia/Seoul",  # 🔧 시간대 정보 추가
                        "last_updated": get_korea_now_iso()
                    }
                }
                
                # SSE 형식으로 전송
                yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                print(f"[ERROR] 위험 직원 데이터 조회 오류: {str(e)}")
                error_data = {
                    "timestamp": get_korea_now_iso(),  # 🔧 한국시간 사용
                    "status": "error",
                    "message": "위험 직원 데이터 조회 중 오류가 발생했습니다.",
                    "details": str(e),  # 🔧 디버깅용 추가
                    "risk_level": "위험"
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            # 5분 대기 (위험자는 더 자주 체크)
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
def caution_employees_stream():
    """
    주의 직원 실시간 스트림 API
    GET /api/web/safety/caution-employees/stream?token=JWT_TOKEN
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    # 앱 인스턴스 생성
    app = create_app()
    
    def generate_caution_stream():
        # 🔧 한국시간으로 초기 연결 메시지
        initial_message = {
            "status": "connected",
            "message": "주의 직원 데이터 스트림 연결 성공",
            "timestamp": get_korea_now_iso(),
            "risk_level": "주의"
        }
        yield f"data: {json.dumps(initial_message, ensure_ascii=False)}\n\n"
        time.sleep(1)
        
        while True:
            try:
                employees_data = get_employees_by_risk_level_data('주의', app.app_context())
                
                # 응답 데이터 생성
                response_data = {
                    "timestamp": get_korea_now_iso(),  # 🔧 한국시간 사용
                    "status": "success",
                    "data": {
                        "risk_level": "주의",
                        "employees": employees_data,
                        "total_count": len(employees_data)  # 🔧 총 인원수 추가
                    },
                    "meta": {
                        "timezone": "Asia/Seoul",  # 🔧 시간대 정보 추가
                        "last_updated": get_korea_now_iso()
                    }
                }
                
                # SSE 형식으로 전송
                yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                
            except Exception as e:
                print(f"[ERROR] 주의 직원 데이터 조회 오류: {str(e)}")
                error_data = {
                    "timestamp": get_korea_now_iso(),  # 🔧 한국시간 사용
                    "status": "error",
                    "message": "주의 직원 데이터 조회 중 오류가 발생했습니다.",
                    "details": str(e),  # 🔧 디버깅용 추가
                    "risk_level": "주의"
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            # 5분 대기 (주의는 조금 덜 자주)
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
