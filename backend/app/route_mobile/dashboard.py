from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.employee import Employee, Admin
from app.models.device import Device, DeviceFailure
from app.models.measurement import DeviceMeasurement, HealthAnomaly
from app.schemas.measurement import HeaderInfoSchema, HeatIncidentSchema, FallIncidentSchema, IncidentTotalSchema, DeviceStatusSchema, WeeklyHeatStatsSchema
from datetime import datetime, timedelta
from sqlalchemy import func

app_dashboard_bp = Blueprint('app/dashboard', __name__)

@app_dashboard_bp.route('/main/weather', methods=['GET'])  # whether -> weather로 수정 (오타 수정)
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