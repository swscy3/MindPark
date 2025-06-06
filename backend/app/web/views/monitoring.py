# app/web/monitoring.py
from flask import Blueprint, Response, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime, timedelta, date
import time
import json
import traceback

# Flask 앱 인스턴스와 DB 세션을 명시적으로 가져오기
from app import create_app, db
from app.model import HealthAnomaly, Employee, Device, DeviceMeasurement, DeviceManagement

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/dashboard/stream')
@jwt_required()
def dashboard_stream():
    """
    대시보드 실시간 모니터링 데이터 스트림 API
    GET /api/web/monitoring/dashboard/stream
    """
    # 앱 인스턴스 생성 - create_app 함수가 정의되어 있어야 함
    app = create_app()
    
    def generate_dashboard_stream():
        # 초기 연결 메시지
        yield "data: {\"status\":\"connected\",\"message\":\"대시보드 모니터링 스트림 연결 성공\"}\n\n"
        time.sleep(1)
        
        while True:
            # 각 반복마다 새로운 앱 컨텍스트 생성
            with app.app_context():
                try:
                    # 1. 온열질환 위험자 조회
                    heat_risks = db.session.query(HealthAnomaly, Employee)\
                        .join(Employee, HealthAnomaly.emp_id == Employee.emp_id)\
                        .filter(HealthAnomaly.symptom == '온열질환')\
                        .filter(HealthAnomaly.status == '처리중')\
                        .all()
                    
                    heat_risk_data = []
                    for anomaly, employee in heat_risks:
                        # 최신 생체 데이터 조회
                        latest_measurement = DeviceMeasurement.query\
                            .filter_by(emp_id=employee.emp_id)\
                            .order_by(DeviceMeasurement.measure_time.desc())\
                            .first()
                        
                        heat_risk_data.append({
                            "emp_id": employee.emp_id,
                            "name": employee.name,
                            "picture": employee.picture,
                            "vitals": {
                                "temperature": latest_measurement.temp if latest_measurement else None,
                                "heart_rate": latest_measurement.hr if latest_measurement else None,
                                "respiration": latest_measurement.resp if latest_measurement else None
                            },
                            "risk_level": anomaly.risk,
                            "location": {
                                "latitude": anomaly.loc_x,
                                "longitude": anomaly.loc_y
                            },
                            "detected_time": anomaly.anomaly_time.isoformat() if anomaly.anomaly_time else None
                        })
                    
                    # 2. 낙상 위험자 조회
                    fall_risks = db.session.query(HealthAnomaly, Employee)\
                        .join(Employee, HealthAnomaly.emp_id == Employee.emp_id)\
                        .filter(HealthAnomaly.symptom == '낙상')\
                        .filter(HealthAnomaly.status == '처리중')\
                        .all()
                    
                    fall_risk_data = []
                    for anomaly, employee in fall_risks:
                        # 최신 생체 데이터 조회
                        latest_measurement = DeviceMeasurement.query\
                            .filter_by(emp_id=employee.emp_id)\
                            .order_by(DeviceMeasurement.measure_time.desc())\
                            .first()
                        
                        fall_risk_data.append({
                            "emp_id": employee.emp_id,
                            "name": employee.name,
                            "picture": employee.picture,
                            "vitals": {
                                "temperature": latest_measurement.temp if latest_measurement else None,
                                "heart_rate": latest_measurement.hr if latest_measurement else None,
                                "respiration": latest_measurement.resp if latest_measurement else None
                            },
                            "risk_level": anomaly.risk,
                            "location": {
                                "latitude": anomaly.loc_x,
                                "longitude": anomaly.loc_y
                            },
                            "detected_time": anomaly.anomaly_time.isoformat() if anomaly.anomaly_time else None
                        })
                    
                    # 3. 장비 현황 조회 (출근 기반)
                    total_devices = Device.query.count()
                    
                    # 오늘 날짜
                    today = date.today()
                    
                    # 활성 장비: 오늘 출근했고 아직 퇴근하지 않은 직원의 장비
                    active_devices = db.session.query(Device.device_id)\
                        .join(DeviceManagement, Device.device_id == DeviceManagement.device_id)\
                        .filter(db.func.date(DeviceManagement.check_in) == today)\
                        .filter(DeviceManagement.check_out.is_(None))\
                        .distinct().count()
                    
                    inactive_devices = total_devices - active_devices
                    
                    # 4. 응답 데이터 생성
                    response_data = {
                        "timestamp": datetime.now().isoformat(),
                        "status": "success",
                        "data": {
                            "heat_risk_employees": heat_risk_data,
                            "fall_risk_employees": fall_risk_data,
                            "device_status": {
                                "total_devices": total_devices,
                                "active_devices": active_devices,
                                "inactive_devices": inactive_devices,
                                "last_updated": datetime.now().isoformat()
                            }
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
            
            # 앱 컨텍스트 외부에서 sleep
            time.sleep(300)  # 5분 대기
    
    return Response(
        generate_dashboard_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Content-Type': 'text/event-stream',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )