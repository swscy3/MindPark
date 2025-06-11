# app/web/monitoring.py
from flask import Blueprint, Response, jsonify, request
from datetime import datetime, date
import time
import json

from app import create_app, db
from app.model import HealthAnomaly, Employee, Device, DeviceMeasurement, DeviceManagement

from app.util.auth import verify_token_from_query
from app.util.time_utils import (  # 🔧 한국시간 유틸리티 추가
    get_korea_today, 
    get_korea_now_iso, 
    to_korea_time,
    utc_to_korea_date
)

monitoring_bp = Blueprint('monitoring', __name__)

def get_active_devices_count(korea_today):
    """
    한국시간 기준으로 활성 디바이스 수 계산
    
    Args:
        korea_today (date): 한국시간 기준 오늘 날짜
        
    Returns:
        int: 활성 디바이스 수
    """
    try:
        # 모든 디바이스 관리 레코드 조회
        device_managements = DeviceManagement.query.all()
        
        active_device_ids = set()
        
        for dm in device_managements:
            if dm.check_in:
                # UTC 시간을 한국 날짜로 변환
                check_in_korea_date = utc_to_korea_date(dm.check_in)
                
                # 한국시간 기준으로 오늘 출근했고 아직 퇴근하지 않았다면
                if (check_in_korea_date == korea_today and 
                    dm.check_out is None):
                    active_device_ids.add(dm.device_id)
        
        return len(active_device_ids)
        
    except Exception as e:
        print(f"[ERROR] 활성 디바이스 수 계산 오류: {str(e)}")
        return 0

@monitoring_bp.route('/dashboard/stream')
def dashboard_stream():
    """
    대시보드 모니터링 스트림 API
    GET /api/web/monitoring/dashboard/stream?token=JWT_TOKEN
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    app = create_app()
    
    def generate_dashboard_stream():
        # 🔧 한국시간으로 연결 메시지 타임스탬프 수정
        initial_message = {
            "status": "connected",
            "message": "대시보드 모니터링 스트림 연결 성공",
            "timestamp": get_korea_now_iso()
        }
        yield f"data: {json.dumps(initial_message, ensure_ascii=False)}\n\n"
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
                        try:
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
                                "detected_time": to_korea_time(anomaly.anomaly_time),  # 🔧 한국시간 변환
                                "last_measurement_time": to_korea_time(latest_measurement.measure_time) if latest_measurement else None  # 🔧 추가
                            })
                        except Exception as emp_error:
                            print(f"[ERROR] 온열질환 직원 {employee.emp_id} 데이터 처리 오류: {str(emp_error)}")
                            continue
                    
                    # 2. 낙상 위험자 조회
                    fall_risks = db.session.query(HealthAnomaly, Employee)\
                        .join(Employee, HealthAnomaly.emp_id == Employee.emp_id)\
                        .filter(HealthAnomaly.symptom == '낙상')\
                        .filter(HealthAnomaly.status == '처리중')\
                        .all()
                    
                    fall_risk_data = []
                    for anomaly, employee in fall_risks:
                        try:
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
                                "detected_time": to_korea_time(anomaly.anomaly_time),  # 🔧 한국시간 변환
                                "last_measurement_time": to_korea_time(latest_measurement.measure_time) if latest_measurement else None  # 🔧 추가
                            })
                        except Exception as emp_error:
                            print(f"[ERROR] 낙상 직원 {employee.emp_id} 데이터 처리 오류: {str(emp_error)}")
                            continue
                    
                    # 3. 장비 현황 조회 (🔧 한국시간 기준으로 수정)
                    total_devices = Device.query.count()
                    korea_today = get_korea_today()  # 🔧 한국시간 기준 오늘
                    active_devices = get_active_devices_count(korea_today)  # 🔧 수정된 함수 사용
                    inactive_devices = total_devices - active_devices
                    
                    # 4. 응답 데이터 생성
                    current_time = get_korea_now_iso()  # 🔧 한국시간 사용
                    
                    response_data = {
                        "timestamp": current_time,  # 🔧 한국시간으로 수정
                        "status": "success",
                        "data": {
                            "heat_risk_employees": heat_risk_data,
                            "fall_risk_employees": fall_risk_data,
                            "device_status": {
                                "total_devices": total_devices,
                                "active_devices": active_devices,
                                "inactive_devices": inactive_devices,
                                "calculation_date": korea_today.isoformat(),  # 🔧 계산 기준일 추가
                                "last_updated": current_time  # 🔧 한국시간으로 수정
                            }
                        },
                        "debug_info": {
                            "heat_risk_count": len(heat_risk_data),
                            "fall_risk_count": len(fall_risk_data),
                            "timezone": "Asia/Seoul",  # 🔧 시간대 정보 추가
                            "korea_today": korea_today.isoformat()  # 🔧 디버깅용
                        }
                    }

                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                    
                except Exception as e:
                    print(f"[ERROR] 대시보드 데이터 조회 오류: {str(e)}")
                    error_data = {
                        "timestamp": get_korea_now_iso(),  # 🔧 한국시간으로 수정
                        "status": "error", 
                        "message": "대시보드 데이터 조회 중 오류가 발생했습니다.",
                        "details": str(e)  # 🔧 디버깅용 추가
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
