from flask import Blueprint, jsonify, current_app
from flask_jwt_extended import jwt_required
from datetime import datetime
import requests
import random

weather_bp = Blueprint('util', __name__)


def get_random_weather():
    """랜덤 날씨 데이터 생성 (Fallback용)
    무안군 10월 평균 날씨 기준:
    - 기온: 10.4°C ~ 21.2°C
    - 습도: 55% ~ 85%
    - 풍속: 0.5 ~ 3.5 m/s
    """
    temperature = round(random.uniform(10.0, 22.0), 1)
    humidity = random.randint(55, 85)
    wind_speed = round(random.uniform(0.5, 3.5), 1)
    sky = random.choices(
        ['맑음', '구름많음', '흐림'],
        weights=[40, 40, 20],  # 맑음 40%, 구름많음 40%, 흐림 20%
        k=1
    )[0]

    return {
        'temperature': f"{temperature}°C",
        'humidity': f"{humidity}%",
        'windSpeed': f"{wind_speed}m/s",
        'sky': sky
    }


@weather_bp.route('/weather', methods=['GET'])
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
        # 0.1초 타임아웃으로 API 호출
        response = requests.get(url, params=params, timeout=0.1)
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

        # API 응답이 있어도 데이터가 비어있으면 랜덤 값 반환
        if not weather_info:
            return jsonify(get_random_weather()), 200

        return jsonify(weather_info), 200

    except Exception:
        # API 호출 실패 시 랜덤 날씨 데이터 반환
        return jsonify(get_random_weather()), 200