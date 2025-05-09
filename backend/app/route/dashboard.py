from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.employee import Employee, Admin
from app.models.device import Device, DeviceFailure
from app.models.measurement import DeviceMeasurement, HealthAnomaly
from app.schemas.measurement import HeaderInfoSchema, HeatIncidentSchema, FallIncidentSchema, IncidentTotalSchema, DeviceStatusSchema, WeeklyHeatStatsSchema
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/main/header', methods=['GET'])
@jwt_required()
def get_header_info():
    """대시보드 헤더 정보를 반환합니다."""
    # 관리자 정보 가져오기
    admin = Admin.query.join(Employee).first()
    
    # 응답 데이터 구성
    header_data = {
        "man_name": admin.employee.name if admin else "관리자",
        "man_photo": "/images/admin.jpg",
        "site_temp": 28.5,  # 실제 구현에서는 환경 센서 데이터에서 가져와야 함
        "site_humi": 65.2,
        "site_wind": 1.4,
        "notice_title": ["안전모 착용 필수", "5월 정기 점검 안내"]
    }
    
    schema = HeaderInfoSchema()
    return jsonify(schema.dump(header_data)), 200

@dashboard_bp.route('/main/heat_incident', methods=['GET'])
@jwt_required()
def get_heat_incidents():
    """온열질환 이상자 정보를 반환합니다."""
    # 현재 온열질환 이상자 조회
    today = datetime.now().date()
    heat_anomalies = HealthAnomaly.query.filter(
        func.date(HealthAnomaly.anomaly_time) == today,
        HealthAnomaly.symptom.like('%온열%')
    ).join(Employee).all()
    
    # 응답 데이터 구성
    heat_data = {
        "heat_name": [],
        "heat_temp": [],
        "heat_hr": [],
        "heat_risk": [],
        "heat_incident_lat": [],
        "heat_incident_lng": []
    }
    
    for anomaly in heat_anomalies:
        # 가장 최근 측정 데이터 조회
        measurement = DeviceMeasurement.query.filter_by(emp_id=anomaly.emp_id).order_by(DeviceMeasurement.measure_time.desc()).first()
        
        if measurement:
            heat_data["heat_name"].append(anomaly.employee.name)
            heat_data["heat_temp"].append(str(measurement.temp))
            heat_data["heat_hr"].append(str(measurement.hr))
            heat_data["heat_risk"].append(anomaly.risk)
            heat_data["heat_incident_lat"].append(anomaly.loc_x)
            heat_data["heat_incident_lng"].append(anomaly.loc_y)
    
    # 테스트 데이터가 없는 경우를 위한 임시 데이터
    if not heat_data["heat_name"]:
        heat_data = {
            "heat_name": ["김철수", "이영희"],
            "heat_temp": ["38.2", "37.9"],
            "heat_hr": ["120", "115"],
            "heat_risk": ["위험", "경고"],
            "heat_incident_lat": [37.532, 37.535],
            "heat_incident_lng": [127.123, 127.125]
        }
    
    schema = HeatIncidentSchema()
    return jsonify(schema.dump(heat_data)), 200

@dashboard_bp.route('/main/fall_incident', methods=['GET'])
@jwt_required()
def get_fall_incidents():
    """낙상 이상자 정보를 반환합니다."""
    # 현재 낙상 이상자 조회
    today = datetime.now().date()
    fall_anomalies = HealthAnomaly.query.filter(
        func.date(HealthAnomaly.anomaly_time) == today,
        HealthAnomaly.symptom.like('%낙상%')
    ).join(Employee).all()
    
    # 응답 데이터 구성
    fall_data = {
        "fall_name": [],
        "fall_temp": [],
        "fall_hr": [],
        "fall_state": [],
        "fall_incident_lat": [],
        "fall_incident_lng": []
    }
    
    for anomaly in fall_anomalies:
        # 가장 최근 측정 데이터 조회
        measurement = DeviceMeasurement.query.filter_by(emp_id=anomaly.emp_id).order_by(DeviceMeasurement.measure_time.desc()).first()
        
        if measurement:
            fall_data["fall_name"].append(anomaly.employee.name)
            fall_data["fall_temp"].append(str(measurement.temp))
            fall_data["fall_hr"].append(str(measurement.hr))
            fall_data["fall_state"].append(anomaly.risk)
            fall_data["fall_incident_lat"].append(anomaly.loc_x)
            fall_data["fall_incident_lng"].append(anomaly.loc_y)
    
    # 테스트 데이터가 없는 경우를 위한 임시 데이터
    if not fall_data["fall_name"]:
        fall_data = {
            "fall_name": ["박지민"],
            "fall_temp": ["36.7"],
            "fall_hr": ["85"],
            "fall_state": ["가벼움"],
            "fall_incident_lat": [37.534],
            "fall_incident_lng": [127.127]
        }
    
    schema = FallIncidentSchema()
    return jsonify(schema.dump(fall_data)), 200

@dashboard_bp.route('/main/incident_total', methods=['GET'])
@jwt_required()
def get_incident_total():
    """이상자 총 인원을 반환합니다."""
    # 오늘의 이상자 수 조회
    today = datetime.now().date()
    
    heat_count = HealthAnomaly.query.filter(
        func.date(HealthAnomaly.anomaly_time) == today,
        HealthAnomaly.symptom.like('%온열%')
    ).count()
    
    fall_count = HealthAnomaly.query.filter(
        func.date(HealthAnomaly.anomaly_time) == today,
        HealthAnomaly.symptom.like('%낙상%')
    ).count()
    
    # 테스트 데이터가 없는 경우를 위한 임시 데이터
    if heat_count == 0 and fall_count == 0:
        heat_count = 2
        fall_count = 1
    
    data = {
        "heat_incident_total": heat_count,
        "fall_incident_total": fall_count
    }
    
    schema = IncidentTotalSchema()
    return jsonify(schema.dump(data)), 200

@dashboard_bp.route('/main/device_status', methods=['GET'])
@jwt_required()
def get_device_status():
    """기기 상태 정보를 반환합니다."""
    # 기기 수량 조회
    total_devices = Device.query.count()
    
    # 현재 오류 상태인 기기 수 (최근 7일 이내 고장 발생)
    one_week_ago = datetime.now() - timedelta(days=7)
    error_devices = DeviceFailure.query.filter(
        DeviceFailure.fail_time >= one_week_ago
    ).with_entities(DeviceFailure.device_id).distinct().count()
    
    # 정상 기기 수
    active_devices = total_devices - error_devices
    
    # 테스트 데이터가 없는 경우를 위한 임시 데이터
    if total_devices == 0:
        total_devices = 50
        active_devices = 47
        error_devices = 3
    
    data = {
        "device_total": total_devices,
        "device_active": active_devices,
        "device_error": error_devices
    }
    
    schema = DeviceStatusSchema()
    return jsonify(schema.dump(data)), 200

@dashboard_bp.route('/main/weekly_heat_stats', methods=['GET'])
@jwt_required()
def get_weekly_heat_stats():
    """주간 온열질환자 통계를 반환합니다."""
    today = datetime.now().date()
    stats = {
        "heat_week_4": 0,
        "heat_week_3": 0,
        "heat_week_2": 0,
        "heat_week_1": 0,
        "heat_week_0": 0
    }
    
    # 각 주차별 온열질환자 수 조회
    for i in range(5):
        week_start = today - timedelta(days=today.weekday() + 7 * i)
        week_end = week_start + timedelta(days=6)
        
        count = HealthAnomaly.query.filter(
            func.date(HealthAnomaly.anomaly_time) >= week_start,
            func.date(HealthAnomaly.anomaly_time) <= week_end,
            HealthAnomaly.symptom.like('%온열%')
        ).count()
        
        stats[f"heat_week_{4-i}"] = count
    
    # 테스트 데이터가 없는 경우를 위한 임시 데이터
    if all(value == 0 for value in stats.values()):
        stats = {
            "heat_week_4": 1,
            "heat_week_3": 2,
            "heat_week_2": 3,
            "heat_week_1": 1,
            "heat_week_0": 2
        }
    
    schema = WeeklyHeatStatsSchema()
    return jsonify(schema.dump(stats)), 200


@dashboard_bp.route('/main/weather', methods=['GET'])  # whether -> weather로 수정 (오타 수정)
@jwt_required()
def get_weather():
    from flask import current_app, jsonify
    from datetime import datetime
    import requests
    
    # 기본 파라미터 가져오기
    url = current_app.config['WHETHER_API_URL']
    key = current_app.config['WHETHER_API_KEY']
    nx = current_app.config['NX']
    ny = current_app.config['NY']
    
    # 현재 날짜와 시간 포맷팅
    current_date = datetime.now().strftime('%Y%m%d')
    current_time = datetime.now().strftime('%H%M')
    
    params = {
        'serviceKey': key,
        'pageNo': '1',
        'numOfRows': '1000',
        'dataType': 'JSON',
        'base_date': current_date,
        'base_time': current_time,
        'nx': nx,
        'ny': ny 
    }
    
    try:
        # 외부 API 호출
        response = requests.get(url, params=params)
        response.raise_for_status()  # HTTP 오류 발생 시 예외 발생
        
        data = response.json()
        
        # 필요한 카테고리만 필터링
        weather_data = {}
        
        for item in data['response']['body']['items']['item']:
            category = item['category']
            
            if category in ['T1H', 'REH', 'WSD']:
                # 카테고리별 데이터 저장
                if category == 'T1H':
                    weather_data['temperature'] = item['obsrValue'] + '°C'
                elif category == 'REH':
                    weather_data['humidity'] = item['obsrValue'] + '%'
                elif category == 'WSD':
                    weather_data['windSpeed'] = item['obsrValue'] + 'm/s'
        
        # 결과 JSON 생성
        result = {
            'status': 'success',
            'baseDate': current_date,
            'baseTime': current_time,
            'nx': nx,
            'ny': ny,
            'weather': weather_data
        }
        
        # JSON 응답 반환
        return jsonify(result), 200
        
    except requests.exceptions.RequestException as e:
        # API 요청 오류 처리
        current_app.logger.error(f"날씨 API 호출 오류: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '날씨 정보를 가져오는 중 오류가 발생했습니다.'
        }), 500
        
    except (ValueError, KeyError) as e:
        # JSON 파싱 또는 데이터 추출 오류 처리
        current_app.logger.error(f"날씨 데이터 처리 오류: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '날씨 데이터를 처리하는 중 오류가 발생했습니다.'
        }), 500