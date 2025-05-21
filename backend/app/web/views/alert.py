# app/web/alert.py
from flask import Blueprint, Response, current_app, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import time
import json
import traceback

# Flask 앱 인스턴스와 DB 세션을 명시적으로 가져오기
from app import create_app, db
from app.model import HealthAnomaly

alert_bp = Blueprint('alert_bp', __name__)

@alert_bp.route('/anomalies/stream')
@jwt_required(optional=True)
def health_anomaly_stream():
    """
    건강 이상 감지 데이터 실시간 스트림 API
    GET /api/web/alert/anomalies/stream
    """
    # 앱 인스턴스 생성 - create_app 함수가 정의되어 있어야 함
    app = create_app()
    
    def generate_health_anomaly_stream():
        # 초기 연결 메시지
        yield "data: {\"status\":\"connected\",\"message\":\"건강 이상 감지 데이터 스트림 연결 성공\"}\n\n"
        time.sleep(1)
        
        while True:
            # 각 반복마다 새로운 앱 컨텍스트 생성
            with app.app_context():
                try:
                    # 현재 사용자 확인 시도
                    try:
                        current_user = get_jwt_identity()
                    except:
                        current_user = None
                    
                    # HealthAnomaly 테이블의 모든 데이터 조회
                    all_anomalies = HealthAnomaly.query.options(db.joinedload(HealthAnomaly.employee)).all()
                    
                    # 데이터 변환
                    formatted_data = []
                    for anomaly in all_anomalies:
                        employee_name = anomaly.employee.name if anomaly.employee else '알 수 없음'
                        
                        formatted_item = {
                            'anomaly_id': anomaly.anomaly_id,
                            'emp_id': anomaly.emp_id,
                            'emp_name': employee_name,
                            'symptom': anomaly.symptom,
                            'location': {
                                'x': anomaly.loc_x,
                                'y': anomaly.loc_y
                            },
                            'anomaly_time': anomaly.anomaly_time.isoformat() if anomaly.anomaly_time else None,
                            'status': anomaly.status,
                            'management': {
                                'risk': anomaly.risk,
                                'action_content': anomaly.action_content,
                                'updated_at': anomaly.updated_at.isoformat() if anomaly.updated_at else None
                            }
                        }
                        
                        formatted_data.append(formatted_item)
                    
                    # 응답 데이터 생성
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    response_data = {
                        'status': 'success',
                        'timestamp': current_time,
                        'record_count': len(formatted_data),
                        'data': formatted_data
                    }
                    
                    # JSON 데이터를 SSE 형식으로 변환하여 전송
                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                
                except Exception as e:
                    error_info = {
                        'status': 'error',
                        'message': str(e),
                        'traceback': traceback.format_exc(),
                        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    yield f"data: {json.dumps(error_info, ensure_ascii=False)}\n\n"
            
            # 앱 컨텍스트 외부에서 sleep
            time.sleep(300)  # 5분 대기
    
    return Response(
        generate_health_anomaly_stream(),
        mimetype='text/event-stream', 
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Content-Type': 'text/event-stream',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@alert_bp.route('/anomalies/detail', methods=['GET'])
@jwt_required()
def get_health_anomaly():
    """
    특정 건강 이상 감지 데이터 상세 조회 API
    GET /api/web/alert/anomalies/detail
    
    두 가지 방식으로 요청 가능:
    1. 쿼리 파라미터: /api/web/alert/anomalies/detail?anomaly_id=ANM001
    2. JSON 본문:
    {
        "anomaly_id": "ANM001"
    }
    """
    try:
        # JSON 본문에서 anomaly_id 가져오기 시도
        data = request.get_json(silent=True)  # silent=True로 설정하여 오류 방지
        
        # JSON 본문이 있으면 JSON에서, 없으면 쿼리 파라미터에서 가져옴
        if data and 'anomaly_id' in data:
            anomaly_id = data['anomaly_id']
        else:
            # 쿼리 파라미터 시도
            anomaly_id = request.args.get('anomaly_id')
        
        if not anomaly_id:
            return jsonify({
                'status': 'error',
                'message': 'anomaly_id가 제공되지 않았습니다. JSON 본문 또는 쿼리 파라미터로 제공해주세요.'
            }), 400
            
        # 데이터베이스에서 특정 ID의 건강 이상 데이터 조회
        anomaly = HealthAnomaly.query.options(db.joinedload(HealthAnomaly.employee)).filter_by(anomaly_id=anomaly_id).first()
        
        if not anomaly:
            return jsonify({
                'status': 'error',
                'message': f'ID가 {anomaly_id}인 건강 이상 데이터를 찾을 수 없습니다.'
            }), 404
        
        # employee 관계를 통해 직원 이름 가져오기
        employee_name = anomaly.employee.name if anomaly.employee else '알 수 없음'
        
        # 요청된 필드만 포함하여 응답 생성
        response_data = {
            'anomaly_id': anomaly.anomaly_id,
            'emp_id': anomaly.emp_id,                  # 사번
            'emp_name': employee_name,                 # 이름
            'symptom': anomaly.symptom,                # 증상
            'anomaly_time': anomaly.anomaly_time.isoformat() if anomaly.anomaly_time else None,  # 시간
            'status': anomaly.status,                  # 상태
            'action_content': anomaly.action_content,  # 조치내용
            'risk': anomaly.risk,                      # 추가 정보
            'updated_at': anomaly.updated_at.isoformat() if anomaly.updated_at else None
        }
        
        return jsonify({
            'status': 'success',
            'message': '건강 이상 감지 데이터 조회 성공',
            'data': response_data
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'데이터 조회 중 오류 발생: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

# 건강 이상 감지 데이터 상태 및 조치내용 수정 API
@alert_bp.route('/anomalies/update', methods=['POST'])
@jwt_required()
def update_health_anomaly():
    """
    특정 건강 이상 감지 데이터의 상태 및 조치내용 수정 API
    POST /api/web/alert/anomalies/update
    
    요청 본문:
    {
        "anomaly_id": "ANM001",
        "status": "완료",
        "action_content": "의무실에서 치료 후 안정"
    }
    """
    try:
        # 요청 데이터 검증
        data = request.get_json()
        
        if not data:
            return jsonify({
                'status': 'error',
                'message': '요청 본문이 제공되지 않았습니다.'
            }), 400
        
        # 필수 필드 확인
        if 'anomaly_id' not in data:
            return jsonify({
                'status': 'error',
                'message': '요청 본문에 anomaly_id가 제공되지 않았습니다.'
            }), 400
            
        anomaly_id = data['anomaly_id']
        
        # 수정 가능한 필드 확인
        status = data.get('status')
        action_content = data.get('action_content')
        
        if status is None and action_content is None:
            return jsonify({
                'status': 'error',
                'message': '수정할 필드(status, action_content)가 제공되지 않았습니다.'
            }), 400
            
        # 유효한 상태 값 확인 (status가 제공된 경우)
        if status is not None:
            valid_statuses = ['처리중', '완료']
            if status not in valid_statuses:
                return jsonify({
                    'status': 'error',
                    'message': f'유효하지 않은 상태입니다. 유효한 값: {", ".join(valid_statuses)}'
                }), 400
        
        # 데이터베이스에서 항목 조회
        anomaly = HealthAnomaly.query.filter_by(anomaly_id=anomaly_id).first()
        
        if not anomaly:
            return jsonify({
                'status': 'error',
                'message': f'ID가 {anomaly_id}인 건강 이상 데이터를 찾을 수 없습니다.'
            }), 404
        
        # 현재 사용자 확인 (JWT에서 추출)
        current_user = get_jwt_identity()
        
        # 데이터 업데이트
        if status is not None:
            anomaly.status = status
        if action_content is not None:
            anomaly.action_content = action_content
        
        # 업데이트 시간은 onupdate=datetime.utcnow에 의해 자동으로 업데이트됨
        # 변경 사항 저장
        db.session.commit()
        
        # 수정된 데이터 응답
        response_data = {
            'anomaly_id': anomaly.anomaly_id,
            'status': anomaly.status,
            'action_content': anomaly.action_content,
            'updated_at': anomaly.updated_at.isoformat() if anomaly.updated_at else None,
            'updated_by': current_user
        }
        
        return jsonify({
            'status': 'success',
            'message': '건강 이상 감지 데이터 수정 성공',
            'data': response_data
        }), 200
        
    except Exception as e:
        # 오류 발생 시 트랜잭션 롤백
        db.session.rollback()
        
        return jsonify({
            'status': 'error',
            'message': f'데이터 수정 중 오류 발생: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500