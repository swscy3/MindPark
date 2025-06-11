# app/web/employees.py
from flask import Blueprint, jsonify, Response, request
from datetime import datetime, date, timedelta
import time
import json

# Flask 앱 인스턴스와 DB 세션을 명시적으로 가져오기
from app import create_app, db
from app.model import (
    Employee, EmergencyContact, DeviceMeasurement, 
    Device, DeviceManagement, Admin
)

from app.util.auth import verify_token_from_query
from app.util.time_utils import (  # 🔧 공용 유틸리티 사용
    get_korea_today, 
    get_korea_now_iso, 
    to_korea_time,
    get_korea_datetime
)

employees_bp = Blueprint('employees', __name__)

def get_attendance_status(emp_id, today):
    """출근 상태 확인 (한국 시간 기준)"""
    # 한국 시간 기준으로 날짜 비교
    attendance = DeviceManagement.query\
        .filter_by(emp_id=emp_id)\
        .filter(db.func.date(DeviceManagement.check_in) == today)\
        .filter(DeviceManagement.check_out.is_(None))\
        .first()
    
    return "출근중" if attendance else "미출근"

@employees_bp.route('/debug/attendance/<emp_id>')
def debug_attendance(emp_id):
    """출근 데이터 디버깅용 엔드포인트"""
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    try:
        # 서버 시간 정보
        utc_now = datetime.utcnow()
        korea_now = get_korea_datetime()  # 🔧 공용 유틸리티 사용
        server_today = date.today()
        korea_today = get_korea_today()  # 🔧 공용 유틸리티 사용
        
        # 해당 직원의 출근 기록 조회 (최근 7일)
        recent_attendances = DeviceManagement.query\
            .filter_by(emp_id=emp_id)\
            .filter(DeviceManagement.check_in >= (korea_today - timedelta(days=7)))\
            .order_by(DeviceManagement.check_in.desc())\
            .all()
        
        attendance_records = []
        for att in recent_attendances:
            attendance_records.append({
                "check_in": to_korea_time(att.check_in),  # 🔧 한국시간 변환
                "check_out": to_korea_time(att.check_out),  # 🔧 한국시간 변환
                "check_in_date": att.check_in.date().isoformat() if att.check_in else None
            })
        
        # 오늘 출근 기록 확인
        today_attendance = DeviceManagement.query\
            .filter_by(emp_id=emp_id)\
            .filter(db.func.date(DeviceManagement.check_in) == korea_today)\
            .first()
        
        debug_info = {
            "emp_id": emp_id,
            "server_utc_time": utc_now.isoformat(),
            "korea_time": korea_now.isoformat(),
            "server_today": server_today.isoformat(),
            "korea_today": korea_today.isoformat(),
            "today_attendance_found": today_attendance is not None,
            "today_attendance": {
                "check_in": to_korea_time(today_attendance.check_in) if today_attendance else None,  # 🔧 한국시간 변환
                "check_out": to_korea_time(today_attendance.check_out) if today_attendance else None   # 🔧 한국시간 변환
            } if today_attendance else None,
            "recent_attendances": attendance_records,
            "attendance_status": get_attendance_status(emp_id, korea_today)
        }
        
        return jsonify(debug_info), 200
        
    except Exception as e:
        print(f"[ERROR] 출근 디버깅 오류 (emp_id: {emp_id}): {str(e)}")
        return jsonify({
            "error": "출근 데이터 조회 중 오류가 발생했습니다."
        }), 500

@employees_bp.route('/list/stream')
def employees_list_stream():
    """
    전체 작업자 목록 실시간 스트림 API (Admin 제외)
    GET /api/web/emp/list/stream?token=JWT_TOKEN
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    # 앱 인스턴스 생성
    app = create_app()
    
    def generate_employees_stream():
        # 초기 연결 메시지
        yield "data: {\"status\":\"connected\",\"message\":\"작업자 목록 스트림 연결 성공\"}\n\n"
        time.sleep(1)
        
        while True:
            # 각 반복마다 새로운 앱 컨텍스트 생성
            with app.app_context():
                try:
                    # Admin 제외한 일반 직원만 조회
                    employees = Employee.query\
                        .outerjoin(Admin, Employee.emp_id == Admin.admin_id)\
                        .filter(Admin.admin_id.is_(None))\
                        .all()
                    
                    # 한국 시간 기준 오늘 날짜
                    today = get_korea_today()  # 🔧 공용 유틸리티 사용
                    
                    employees_data = []
                    
                    for employee in employees:
                        # 출근 상태 확인
                        attendance_status = get_attendance_status(employee.emp_id, today)
                        
                        employees_data.append({
                            "emp_id": employee.emp_id,
                            "name": employee.name,
                            "department": employee.dept,
                            "position": employee.position,
                            "attendance_status": attendance_status
                        })
                    
                    # 응답 데이터 생성
                    response_data = {
                        "timestamp": get_korea_now_iso(),  # 🔧 한국시간 ISO 형식
                        "korea_today": today.isoformat(),  # 디버깅용 추가
                        "status": "success",
                        "data": {
                            "employees": employees_data
                        }
                    }
                    
                    # SSE 형식으로 전송
                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                    
                except Exception as e:
                    print(f"[ERROR] 직원 목록 조회 오류: {str(e)}")
                    error_data = {
                        "timestamp": get_korea_now_iso(),  # 🔧 한국시간 ISO 형식
                        "status": "error",
                        "message": "직원 목록 조회 중 오류가 발생했습니다."
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            # 앱 컨텍스트 외부에서 sleep
            time.sleep(300)  # 5분 대기
    
    return Response(
        generate_employees_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Content-Type': 'text/event-stream',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@employees_bp.route('/<emp_id>/detail', methods=['GET'])
def get_employee_detail(emp_id):
    """
    작업자 상세정보 조회 API
    GET /api/web/emp/{emp_id}/detail?token=JWT_TOKEN
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    try:
        # 직원 기본 정보
        employee = Employee.query.filter_by(emp_id=emp_id).first()
        if not employee:
            return jsonify({
                "timestamp": get_korea_now_iso(),  # 🔧 한국시간 ISO 형식
                "status": "error",
                "message": f"사번 {emp_id}인 직원을 찾을 수 없습니다."
            }), 404
        
        # 응급 연락처
        emergency_contact = EmergencyContact.query.filter_by(emp_id=emp_id).first()
        emergency_contact_info = None
        if emergency_contact:
            emergency_contact_info = f"{emergency_contact.contact_name} ({emergency_contact.relation}) - {emergency_contact.contact_phone}"
        
        # 최신 생체 데이터
        latest_measurement = DeviceMeasurement.query\
            .filter_by(emp_id=emp_id)\
            .order_by(DeviceMeasurement.measure_time.desc())\
            .first()
        
        # 디바이스 정보
        device = None
        if latest_measurement:
            device = Device.query.filter_by(device_id=latest_measurement.device_id).first()
        
        # 응답 데이터 생성
        response_data = {
            "timestamp": get_korea_now_iso(),  # 🔧 한국시간 ISO 형식
            "status": "success",
            "data": {
                "name": employee.name,
                "age": employee.age,
                "gender": employee.gender,
                "emergency_contact": emergency_contact_info,
                "heart_rate": latest_measurement.hr if latest_measurement else None,
                "spo2": latest_measurement.spo2 if latest_measurement else None,
                "temperature": latest_measurement.temp if latest_measurement else None,
                "steps": latest_measurement.walk if latest_measurement else None,
                "device_name": device.product if device else None,
                "battery_level": latest_measurement.battery if latest_measurement else None,
                "latitude": latest_measurement.loc_y if latest_measurement else None,   # 위도
                "longitude": latest_measurement.loc_x if latest_measurement else None,  # 경도
                "last_measurement_time": to_korea_time(latest_measurement.measure_time) if latest_measurement else None  # 🔧 추가: 마지막 측정 시간
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"[ERROR] 직원 상세정보 조회 오류 (emp_id: {emp_id}): {str(e)}")
        return jsonify({
            "timestamp": get_korea_now_iso(),  # 🔧 한국시간 ISO 형식
            "status": "error",
            "message": "상세정보 조회 중 오류가 발생했습니다."
        }), 500