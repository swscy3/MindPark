from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import decode_token
from datetime import datetime, date
import time
import json
import traceback

from app import create_app, db
from app.model import HealthAnomaly, Employee, Device, DeviceMeasurement, DeviceManagement

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/dashboard/stream')
def dashboard_stream():
    token = request.args.get('token')
    if not token:
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "message": "인증 토큰이 필요합니다. URL에 ?token=YOUR_JWT_TOKEN을 추가하세요."
        }), 401
    
    try:
        decoded_token = decode_token(token)
    except Exception as e:
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "status": "error",
            "message": "유효하지 않은 토큰입니다.",
            "traceback": str(e)
        }), 401
    
    app = create_app()
    
    def generate_dashboard_stream():
        yield "data: {\"status\":\"connected\",\"message\":\"대시보드 모니터링 스트림 연결 성공\"}\n\n"
        time.sleep(1)
        
        while True:
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
                        latest_measurement = DeviceMeasurement.query\
                            .filter_by(emp_id=employee.emp_id)\
                            .order_by(DeviceMeasurement.measure_time.desc())\
                            .first()
                        
                        heat_risk_data.append({
                            "emp_id": employee.emp_id,
                            "name": employee.name,
                            "picture": employee.picture,
                            "vitals": {
                                "temperature": round(latest_measurement.temp, 1) if latest_measurement and latest_measurement.temp is not None else None,
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
                        latest_measurement = DeviceMeasurement.query\
                            .filter_by(emp_id=employee.emp_id)\
                            .order_by(DeviceMeasurement.measure_time.desc())\
                            .first()
                        
                        fall_risk_data.append({
                            "emp_id": employee.emp_id,
                            "name": employee.name,
                            "picture": employee.picture,
                            "vitals": {
                                "temperature": round(latest_measurement.temp, 1) if latest_measurement and latest_measurement.temp is not None else None,
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
                    
                    # 3. 장비 현황 조회
                    total_devices = Device.query.count()
                    today = date.today()
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
                        },
                        "debug_info": {
                            "heat_risk_count": len(heat_risk_data),
                            "fall_risk_count": len(fall_risk_data),
                            "heat_risk_employees": heat_risk_data,
                            "fall_risk_employees": fall_risk_data
                        }
                    }

                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                    
                except Exception as e:
                    error_data = {
                        "timestamp": datetime.now().isoformat(),
                        "status": "error", 
                        "message": str(e),
                        "traceback": traceback.format_exc()
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
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
