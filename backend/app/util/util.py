from flask import Blueprint, jsonify, current_app, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from datetime import datetime
import requests

util_bp = Blueprint('util', __name__)

@util_bp.route('/weather', methods=['GET'])
@jwt_required()
def get_weather():
    """날씨 정보 조회 API"""
    
    # 설정값 가져오기
    url = current_app.config.get('WEATHER_API_URL')
    key = current_app.config.get('WEATHER_API_KEY')
    nx = current_app.config.get('NX', '60')
    ny = current_app.config.get('NY', '127')
    
    # 현재 날짜/시간
    now = datetime.now()
    base_date = now.strftime('%Y%m%d')
    base_time = now.strftime('%H00')  # 정시 기준
    
    params = {
        'serviceKey': key,
        'pageNo': '1',
        'numOfRows': '100',
        'dataType': 'JSON',
        'base_date': base_date,
        'base_time': base_time,
        'nx': nx,
        'ny': ny
    }
    
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        # 날씨 데이터 추출
        weather_info = {}
        items = data.get('response', {}).get('body', {}).get('items', {}).get('item', [])
        
        # 하늘 상태 코드 매핑
        sky_status_map = {
            '1': '맑음',
            '3': '구름많음', 
            '4': '흐림'
        }
        
        for item in items:
            category = item.get('category')
            value = item.get('obsrValue')
            
            if category == 'T1H':  # 온도
                weather_info['temperature'] = f"{value}°C"
            elif category == 'REH':  # 습도
                weather_info['humidity'] = f"{value}%"
            elif category == 'WSD':  # 풍속
                weather_info['windSpeed'] = f"{value}m/s"
            elif category == 'SKY':  # 하늘 상태
                weather_info['sky'] = sky_status_map.get(value, f"알 수 없음({value})")
        
        return jsonify(weather_info), 200
        
    except Exception as e:
        return jsonify({'error': '날씨 정보를 가져올 수 없습니다'}), 500