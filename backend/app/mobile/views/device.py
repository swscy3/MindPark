from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import uuid

from ...model import DeviceMeasurement, db, Device

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
        
        # 필수 데이터 확인
        if not data or 'product' not in data:
            return jsonify({'error': '디바이스 이름(product)은 필수입니다'}), 400
            
        # 디바이스 이름(product)으로 디바이스 ID 조회
        device = Device.query.filter_by(product=data.get('product')).first()
        
        if not device:
            return jsonify({'error': '해당 디바이스 이름과 일치하는 장치를 찾을 수 없습니다'}), 404
            
        # measurement_id 생성 (현재 시간 + 랜덤 문자열로 고유 ID 생성)
        measurement_id = f"M{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:4]}"
        
        # 현재 시각 설정
        current_time = datetime.now()
        
        # DeviceMeasurement 객체 생성
        measurement = DeviceMeasurement(
            measurement_id=measurement_id,
            emp_id=current_user,  # JWT 토큰에서 추출한 사용자 ID 사용
            device_id=device.device_id,  # 조회한 디바이스 ID 사용
            measure_time=current_time,
            battery=data.get('battery'),
            hr=data.get('hr'),
            temp=data.get('temp'),
            resp=data.get('resp'),
            spo2=data.get('spo2'),
            acc_x=data.get('acc_x'),
            acc_y=data.get('acc_y'),
            acc_z=data.get('acc_z'),
            gyro_x=data.get('gyro_x'),
            gyro_y=data.get('gyro_y'),
            gyro_z=data.get('gyro_z'),
            heat_risk=None,  # 온열질환 위험도는 NULL로 설정
            fall_risk=None,  # 낙상 위험도는 NULL로 설정
            walk=data.get('walk')  # 'work'였던 부분을 'walk'로 수정
        )
        
        # 터미널에 데이터 출력
        print("====== 새로운 측정 데이터 ======")
        print(f"Measurement ID: {measurement.measurement_id}")
        print(f"직원 ID: {measurement.emp_id}")
        print(f"장치 ID: {measurement.device_id}")
        print(f"디바이스 이름: {device.product}")  # 디바이스 이름 출력 추가
        print(f"측정 시간: {measurement.measure_time}")
        print(f"배터리: {measurement.battery}")
        print(f"심박수: {measurement.hr}")
        print(f"체온: {measurement.temp}")
        print(f"호흡수: {measurement.resp}")
        print(f"산소포화도: {measurement.spo2}")
        print(f"가속도 X: {measurement.acc_x}")
        print(f"가속도 Y: {measurement.acc_y}")
        print(f"가속도 Z: {measurement.acc_z}")
        print(f"자이로 X: {measurement.gyro_x}")
        print(f"자이로 Y: {measurement.gyro_y}")
        print(f"자이로 Z: {measurement.gyro_z}")
        print(f"온열질환 위험도: {measurement.heat_risk}")
        print(f"낙상 위험도: {measurement.fall_risk}")
        print(f"걸음수: {measurement.walk}")
        print("==============================")
        
        # DB에 저장하지 않고 성공 응답 반환
        return jsonify({
            'success': True,
            'message': '측정 데이터가 성공적으로 처리되었습니다',
            'measurement_id': measurement_id,
            'device_id': device.device_id  # 응답에 device_id 추가
        }), 200
        
    except Exception as e:
        print(f"에러 발생: {str(e)}")
        return jsonify({'error': f'데이터 처리 중 오류가 발생했습니다: {str(e)}'}), 500