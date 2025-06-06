# app/web/employees.py
from flask import Blueprint, jsonify, Response
from flask_jwt_extended import jwt_required
from datetime import datetime, date
import time
import json
import traceback

from app import db
from app.model import (
    Employee, EmergencyContact, DeviceMeasurement, 
    Device, DeviceManagement
)

employees_bp = Blueprint('employees', __name__)

def get_attendance_status(emp_id, today):
    """출근 상태 확인"""
    attendance = DeviceManagement.query\
        .filter_by(emp_id=emp_id)\
        .filter(db.func.date(DeviceManagement.check_in) == today)\
        .filter(DeviceManagement.check_out.is_(None))\
        .first()
    
    return "출근중" if attendance else "미출근"

@employees_bp.route('/list/stream')
@jwt_required()
def employees_list_stream():
    """
    전체 작업자 목록 실시간 스트림 API
    GET /api/web/employees/list/stream
    """
    def generate_employees_stream():
        # 초기 연결 메시지
        yield "data: {\"status\":\"connected\",\"message\":\"작업자 목록 스트림 연결 성공\"}\n\n"
        time.sleep(1)
        
        while True:
            try:
                # 모든 직원 조회
                employees = Employee.query.all()
                today = date.today()
                
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
            
            # 5분 대기
            time.sleep(300)
    
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
@jwt_required()
def get_employee_detail(emp_id):
    """
    작업자 상세정보 조회 API
    GET /api/web/employees/{emp_id}/detail
    """
    try:
        # 직원 기본 정보
        employee = Employee.query.filter_by(emp_id=emp_id).first()
        if not employee:
            return jsonify({
                "timestamp": datetime.now().isoformat(),
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
            "timestamp": datetime.now().isoformat(),
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
                "latitude": latest_measurement.latitude if latest_measurement else None,
                "longitude": latest_measurement.longitude if latest_measurement else None
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "message": f"상세정보 조회 중 오류 발생: {str(e)}",
            "traceback": traceback.format_exc()
        }), 500