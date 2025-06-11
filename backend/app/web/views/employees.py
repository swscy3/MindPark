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
    get_korea_datetime,
    utc_to_korea_date,
    debug_time_conversion  # 🔧 디버깅용 추가
)

employees_bp = Blueprint('employees', __name__)

def get_attendance_status(emp_id, korea_today):
    """
    출근 상태 확인 (한국 시간 기준)
    
    Args:
        emp_id (str): 직원 ID
        korea_today (date): 한국시간 기준 오늘 날짜
        
    Returns:
        str: "출근중" 또는 "미출근"
    """
    try:
        # 🔧 수정된 부분: UTC 시간을 한국 날짜로 변환하여 비교
        # DeviceManagement의 check_in이 UTC 시간이라고 가정
        attendances = DeviceManagement.query.filter_by(emp_id=emp_id).all()
        
        for attendance in attendances:
            if attendance.check_in:
                # UTC 시간을 한국 날짜로 변환
                check_in_korea_date = utc_to_korea_date(attendance.check_in)
                
                # 한국시간 기준으로 오늘 출근했고 아직 퇴근하지 않았는지 확인
                if (check_in_korea_date == korea_today and 
                    attendance.check_out is None):
                    return "출근중"
        
        return "미출근"
        
    except Exception as e:
        print(f"[ERROR] 출근 상태 확인 오류 (emp_id: {emp_id}): {str(e)}")
        return "미출근"  # 에러 시 기본값

def get_today_attendance_record(emp_id, korea_today):
    """
    오늘 출근 기록 조회 (한국 시간 기준)
    
    Args:
        emp_id (str): 직원 ID
        korea_today (date): 한국시간 기준 오늘 날짜
        
    Returns:
        DeviceManagement: 오늘 출근 기록 또는 None
    """
    try:
        attendances = DeviceManagement.query.filter_by(emp_id=emp_id).all()
        
        for attendance in attendances:
            if attendance.check_in:
                check_in_korea_date = utc_to_korea_date(attendance.check_in)
                if check_in_korea_date == korea_today:
                    return attendance
        
        return None
        
    except Exception as e:
        print(f"[ERROR] 출근 기록 조회 오류 (emp_id: {emp_id}): {str(e)}")
        return None

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
        
        print(f"[DEBUG] 출근 상태 디버깅 - 직원ID: {emp_id}")
        print(f"[DEBUG] UTC 현재시간: {utc_now}")
        print(f"[DEBUG] 한국 현재시간: {korea_now}")
        print(f"[DEBUG] 서버 오늘날짜: {server_today}")
        print(f"[DEBUG] 한국 오늘날짜: {korea_today}")
        
        # 해당 직원의 출근 기록 조회 (최근 7일)
        start_date = korea_today - timedelta(days=7)
        recent_attendances = DeviceManagement.query\
            .filter_by(emp_id=emp_id)\
            .order_by(DeviceManagement.check_in.desc())\
            .limit(20)\
            .all()  # 🔧 더 넓은 범위에서 조회
        
        attendance_records = []
        for att in recent_attendances:
            # 🔧 디버깅 정보 추가
            check_in_korea_date = utc_to_korea_date(att.check_in) if att.check_in else None
            check_out_korea_date = utc_to_korea_date(att.check_out) if att.check_out else None
            
            attendance_records.append({
                "check_in_utc": att.check_in.isoformat() if att.check_in else None,
                "check_in_korea": to_korea_time(att.check_in),  # 🔧 한국시간 변환
                "check_in_korea_date": check_in_korea_date.isoformat() if check_in_korea_date else None,
                "check_out_utc": att.check_out.isoformat() if att.check_out else None,
                "check_out_korea": to_korea_time(att.check_out),  # 🔧 한국시간 변환
                "check_out_korea_date": check_out_korea_date.isoformat() if check_out_korea_date else None,
                "is_today": check_in_korea_date == korea_today if check_in_korea_date else False
            })
        
        # 🔧 새로운 방식으로 오늘 출근 기록 확인
        today_attendance = get_today_attendance_record(emp_id, korea_today)
        
        debug_info = {
            "emp_id": emp_id,
            "server_utc_time": utc_now.isoformat(),
            "korea_time": korea_now.isoformat(),
            "server_today": server_today.isoformat(),
            "korea_today": korea_today.isoformat(),
            "today_attendance_found": today_attendance is not None,
            "today_attendance": {
                "check_in_utc": today_attendance.check_in.isoformat() if today_attendance and today_attendance.check_in else None,
                "check_in_korea": to_korea_time(today_attendance.check_in) if today_attendance and today_attendance.check_in else None,
                "check_out_utc": today_attendance.check_out.isoformat() if today_attendance and today_attendance.check_out else None,
                "check_out_korea": to_korea_time(today_attendance.check_out) if today_attendance and today_attendance.check_out else None
            } if today_attendance else None,
            "recent_attendances": attendance_records,
            "attendance_status": get_attendance_status(emp_id, korea_today),
            "total_records_found": len(attendance_records)
        }
        
        return jsonify(debug_info), 200
        
    except Exception as e:
        print(f"[ERROR] 출근 디버깅 오류 (emp_id: {emp_id}): {str(e)}")
        return jsonify({
            "error": "출근 데이터 조회 중 오류가 발생했습니다.",
            "details": str(e)
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
                    
                    # 🔧 한국 시간 기준 오늘 날짜
                    today = get_korea_today()  # 🔧 공용 유틸리티 사용
                    
                    employees_data = []
                    
                    for employee in employees:
                        try:
                            # 🔧 개선된 출근 상태 확인
                            attendance_status = get_attendance_status(employee.emp_id, today)
                            
                            employees_data.append({
                                "emp_id": employee.emp_id,
                                "name": employee.name,
                                "department": employee.dept,
                                "position": employee.position,
                                "attendance_status": attendance_status
                            })
                        except Exception as emp_error:
                            print(f"[ERROR] 직원 {employee.emp_id} 처리 오류: {str(emp_error)}")
                            # 개별 직원 오류 시에도 계속 진행
                            employees_data.append({
                                "emp_id": employee.emp_id,
                                "name": employee.name,
                                "department": employee.dept,
                                "position": employee.position,
                                "attendance_status": "확인불가"
                            })
                    
                    # 응답 데이터 생성
                    response_data = {
                        "timestamp": get_korea_now_iso(),  # 🔧 한국시간 ISO 형식
                        "korea_today": today.isoformat(),  # 디버깅용 추가
                        "status": "success",
                        "data": {
                            "employees": employees_data,
                            "total_count": len(employees_data)  # 🔧 추가 정보
                        }
                    }
                    
                    # SSE 형식으로 전송
                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                    
                except Exception as e:
                    print(f"[ERROR] 직원 목록 조회 오류: {str(e)}")
                    error_data = {
                        "timestamp": get_korea_now_iso(),  # 🔧 한국시간 ISO 형식
                        "status": "error",
                        "message": "직원 목록 조회 중 오류가 발생했습니다.",
                        "details": str(e)  # 🔧 디버깅용 추가
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
        
        # 🔧 최신 생체 데이터 (더 상세한 조회)
        latest_measurement = DeviceMeasurement.query\
            .filter_by(emp_id=emp_id)\
            .order_by(DeviceMeasurement.measure_time.desc())\
            .first()
        
        # 디바이스 정보
        device = None
        if latest_measurement:
            device = Device.query.filter_by(device_id=latest_measurement.device_id).first()
        
        # 🔧 출근 상태 추가
        korea_today = get_korea_today()
        attendance_status = get_attendance_status(emp_id, korea_today)
        
        # 응답 데이터 생성
        response_data = {
            "timestamp": get_korea_now_iso(),  # 🔧 한국시간 ISO 형식
            "status": "success",
            "data": {
                "basic_info": {
                    "emp_id": employee.emp_id,
                    "name": employee.name,
                    "age": employee.age,
                    "gender": employee.gender,
                    "department": employee.dept,
                    "position": employee.position
                },
                "contact_info": {
                    "emergency_contact": emergency_contact_info
                },
                "health_data": {
                    "heart_rate": latest_measurement.hr if latest_measurement else None,
                    "spo2": latest_measurement.spo2 if latest_measurement else None,
                    "temperature": latest_measurement.temp if latest_measurement else None,
                    "steps": latest_measurement.walk if latest_measurement else None,
                    "last_measurement_time": to_korea_time(latest_measurement.measure_time) if latest_measurement else None  # 🔧 한국시간 변환
                },
                "device_info": {
                    "device_name": device.product if device else None,
                    "battery_level": latest_measurement.battery if latest_measurement else None
                },
                "location_info": {
                    "latitude": latest_measurement.loc_y if latest_measurement else None,   # 위도
                    "longitude": latest_measurement.loc_x if latest_measurement else None  # 경도
                },
                "attendance_info": {
                    "status": attendance_status,
                    "check_date": korea_today.isoformat()
                }
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"[ERROR] 직원 상세정보 조회 오류 (emp_id: {emp_id}): {str(e)}")
        return jsonify({
            "timestamp": get_korea_now_iso(),  # 🔧 한국시간 ISO 형식
            "status": "error",
            "message": "상세정보 조회 중 오류가 발생했습니다.",
            "details": str(e)  # 🔧 디버깅용 추가
        }), 500

# 🔧 추가: 출근 기록 조회 API
@employees_bp.route('/<emp_id>/attendance/recent', methods=['GET'])
def get_recent_attendance(emp_id):
    """
    최근 출근 기록 조회 API
    GET /api/web/emp/{emp_id}/attendance/recent?token=JWT_TOKEN&days=7
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    try:
        # 조회할 일수 (기본값: 7일)
        days = int(request.args.get('days', 7))
        if days > 30:  # 최대 30일
            days = 30
        
        # 직원 존재 확인
        employee = Employee.query.filter_by(emp_id=emp_id).first()
        if not employee:
            return jsonify({
                "timestamp": get_korea_now_iso(),
                "status": "error",
                "message": f"사번 {emp_id}인 직원을 찾을 수 없습니다."
            }), 404
        
        # 한국시간 기준 기간 설정
        korea_today = get_korea_today()
        start_date = korea_today - timedelta(days=days-1)
        
        # 출근 기록 조회
        attendances = DeviceManagement.query\
            .filter_by(emp_id=emp_id)\
            .order_by(DeviceManagement.check_in.desc())\
            .all()
        
        # 기간별 출근 기록 필터링 및 포맷팅
        attendance_records = []
        for att in attendances:
            if att.check_in:
                check_in_korea_date = utc_to_korea_date(att.check_in)
                if check_in_korea_date and start_date <= check_in_korea_date <= korea_today:
                    attendance_records.append({
                        "date": check_in_korea_date.isoformat(),
                        "check_in": to_korea_time(att.check_in),
                        "check_out": to_korea_time(att.check_out),
                        "status": "퇴근완료" if att.check_out else "출근중"
                    })
        
        # 날짜순 정렬 (최신순)
        attendance_records.sort(key=lambda x: x['date'], reverse=True)
        
        response_data = {
            "timestamp": get_korea_now_iso(),
            "status": "success",
            "data": {
                "emp_id": emp_id,
                "emp_name": employee.name,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": korea_today.isoformat(),
                    "days": days
                },
                "attendance_records": attendance_records,
                "total_records": len(attendance_records)
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"[ERROR] 출근 기록 조회 오류 (emp_id: {emp_id}): {str(e)}")
        return jsonify({
            "timestamp": get_korea_now_iso(),
            "status": "error",
            "message": "출근 기록 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), 500