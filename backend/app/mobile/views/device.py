from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

from ...model import Device, DeviceMeasurement
from app.mobile.service.device_service import DeviceService

# Blueprint 생성
device_bp = Blueprint('device', __name__, url_prefix='/api/device')

@device_bp.route('/measurement', methods=['POST'])
@jwt_required()  # JWT 토큰 인증 요구
def record_measurement():
    """
    앱에서 측정 데이터를 받아 처리
    - JWT 인증 필요
    - 디바이스 이름(product)으로 device_id 조회
    - measurement_id 생성
    - 현재 시각 설정
    - 위험도 NULL로 설정
    - 터미널에 출력
    """
    try:
        # JWT 토큰에서 사용자 ID 추출
        current_user = get_jwt_identity()

        # 요청에서 데이터 추출
        data = request.get_json()

        # data가 None인 경우 빈 딕셔너리로 초기화
        if not data:
            data = {}

        # product가 없을 경우 하드코딩된 기본값 사용
        product_name = data.get('product', 'Galaxy Watch Active 2')  # 여기에 실제 사용할 디바이스 이름을 넣으세요
        
        print(f"사용할 product: {product_name}")  # 디버깅용 출력

        # 디바이스 이름(product)으로 디바이스 ID 조회
        device = Device.query.filter_by(product=product_name).first()

        if not device:
            return jsonify({'error': f'디바이스 이름 "{product_name}"과 일치하는 장치를 찾을 수 없습니다'}), 404

        # ✅ 서비스 함수 호출
        result = DeviceService.process_measurement(current_user, device, data)

        if result['status'] == 'error':
            return jsonify({'error': result['message']}), 400

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': f'데이터 처리 중 오류가 발생했습니다: {str(e)}'}), 500