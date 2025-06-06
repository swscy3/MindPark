from flask import Blueprint, jsonify, current_app, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from datetime import datetime
import traceback
import time
import json
import os

from app.model import HealthAnomaly

# 블루프린트 정의
debug_bp = Blueprint('debug', __name__)

@debug_bp.route('/test', methods=['GET'])
def test_endpoint():
    """간단한 서버 연결 테스트"""
    return jsonify({
        "message": "테스트 성공",
        "timestamp": datetime.now().isoformat()
    }), 200

@debug_bp.route('/jwt-test', methods=['GET'])
@jwt_required()
def jwt_test():
    """JWT 토큰 검증 테스트"""
    try:
        current_user = get_jwt_identity()
        jwt_data = get_jwt()
        return jsonify({
            "message": "JWT 테스트 성공",
            "user": current_user,
            "jwt_claims": jwt_data
        }), 200
    except Exception as e:
        return jsonify({"error": f"JWT 오류: {str(e)}"}), 500

@debug_bp.route('/routes')
def list_routes():
    """등록된 모든 라우트 목록 조회"""
    routes = []
    for rule in current_app.url_map.iter_rules():
        methods = list(rule.methods - {'HEAD', 'OPTIONS'})
        routes.append({
            'endpoint': rule.endpoint,
            'methods': methods,
            'path': rule.rule
        })
    return jsonify(routes)

@debug_bp.route('/get-token', methods=['GET', 'POST'])
def get_debug_token():
    """
    디버깅용 JWT 토큰 발급 (개발/테스트 전용)
    GET /api/debug/get-token
    """
    # 더미 사용자 ID (원하는 값으로 변경 가능)
    test_user_id = request.args.get('user_id', 'TEST_USER')
    
    # JWT 토큰 생성
    access_token = create_access_token(identity=test_user_id)
    
    return jsonify({
        "message": "디버그용 토큰 발급 성공",
        "token": access_token,
        "user_id": test_user_id,
        "warning": "⚠️ 개발/테스트 전용입니다. 운영환경에서는 제거하세요!"
    }), 200

@debug_bp.route('/health-anomaly-debug', methods=['GET'])
def debug_health_anomaly():
    """HealthAnomaly 모델의 데이터 구조와 샘플 레코드 확인"""
    try:
        # 샘플 레코드 가져오기
        alerts = HealthAnomaly.query.limit(5).all()
        
        # 상세 정보 구성
        debug_data = []
        
        for alert in alerts:
            # 각 필드의 타입과 값 확인
            field_info = {
                'anomaly_id': {
                    'value': alert.anomaly_id,
                    'type': type(alert.anomaly_id).__name__,
                    'is_none': alert.anomaly_id is None
                },
                'emp_id': {
                    'value': alert.emp_id,
                    'type': type(alert.emp_id).__name__,
                    'is_none': alert.emp_id is None
                },
                'anomaly_time': {
                    'value': str(alert.anomaly_time) if alert.anomaly_time else None,
                    'type': type(alert.anomaly_time).__name__ if alert.anomaly_time else 'None',
                    'is_none': alert.anomaly_time is None
                },
                'symptom': {
                    'value': alert.symptom,
                    'type': type(alert.symptom).__name__,
                    'is_none': alert.symptom is None
                },
                'risk': {
                    'value': alert.risk,
                    'type': type(alert.risk).__name__,
                    'is_none': alert.risk is None
                },
                'status': {
                    'value': alert.status,
                    'type': type(alert.status).__name__ if alert.status else 'None',
                    'is_none': alert.status is None
                },
                'action_content': {
                    'value': alert.action_content,
                    'type': type(alert.action_content).__name__ if alert.action_content else 'None',
                    'is_none': alert.action_content is None
                },
                'updated_at': {
                    'value': str(alert.updated_at) if alert.updated_at else None,
                    'type': type(alert.updated_at).__name__ if alert.updated_at else 'None',
                    'is_none': alert.updated_at is None
                }
            }
            
            debug_data.append({
                'anomaly_id': alert.anomaly_id,
                'field_details': field_info
            })
        
        # 모델 필드 타입 정보 포함
        model_fields = {}
        for column in HealthAnomaly.__table__.columns:
            model_fields[column.name] = {
                'type': str(column.type),
                'nullable': column.nullable,
                'default': str(column.default) if column.default else None
            }
            
        return jsonify({
            'message': '데이터베이스 디버그 정보',
            'record_count': len(alerts),
            'sample_records': debug_data,
            'model_definition': model_fields
        }), 200
            
    except Exception as e:
        return jsonify({
            'message': f'디버그 중 오류 발생: {str(e)}',
            'traceback': traceback.format_exc()
        }), 500

@debug_bp.route('/sse-test-long')
def sse_test_long():
    """무한 루프로 실행되는 SSE 테스트 엔드포인트"""
    def infinite_stream():
        # 초기 연결 메시지
        yield "data: 연결 성공\n\n"
        time.sleep(1)
        
        # 무한 루프로 메시지 계속 전송
        counter = 0
        while True:
            counter += 1
            
            # 5초마다 메시지 전송
            current_time = datetime.now().strftime("%H:%M:%S")
            yield f"data: 메시지 #{counter} - {current_time}\n\n"
            
            # 짧은 간격의 sleep (5초)
            # 너무 긴 sleep은 다른 프록시 서버들이 연결을 끊을 수 있음
            time.sleep(5)
    
    return Response(
        infinite_stream(),
        mimetype='text/event-stream', 
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Content-Type': 'text/event-stream',
            'X-Accel-Buffering': 'no',  # Nginx 버퍼링 방지
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@debug_bp.route('/picture-test', methods=['GET'])
def picture_debug():
    """사진 경로 디버깅용 엔드포인트"""
    
    # 현재 경로 정보
    current_file = __file__
    current_dir = os.path.dirname(__file__)
    app_dir = os.path.dirname(os.path.dirname(__file__))  # app 디렉토리
    
    # 여러 가지 가능한 경로들 테스트
    possible_paths = [
        os.path.join(app_dir, '../database/picture'),
        os.path.join(app_dir, '../../database/picture'), 
        os.path.join(app_dir, '../../../database/picture'),
        '/root/MindPark/database/picture',
        '/root/database/picture',
        os.path.join(os.getcwd(), 'database/picture'),
        os.path.join(os.getcwd(), '../database/picture')
    ]
    
    results = []
    working_path = None
    
    for path in possible_paths:
        abs_path = os.path.abspath(path)
        exists = os.path.exists(abs_path)
        files = []
        file_count = 0
        
        if exists:
            try:
                all_files = os.listdir(abs_path)
                file_count = len(all_files)
                files = all_files[:5]  # 처음 5개 파일만
                if not working_path:  # 첫 번째로 작동하는 경로 저장
                    working_path = abs_path
            except Exception as e:
                files = [f"권한 없음: {str(e)}"]
        
        results.append({
            "relative_path": path,
            "absolute_path": abs_path,
            "exists": exists,
            "file_count": file_count,
            "sample_files": files
        })
    
    # 특정 파일 테스트 (woman8 파일 찾기)
    test_files = ['woman8', 'woman8.jpg', 'woman8.png']
    file_tests = []
    
    if working_path:
        for test_file in test_files:
            file_path = os.path.join(working_path, test_file)
            file_tests.append({
                "filename": test_file,
                "full_path": file_path,
                "exists": os.path.exists(file_path),
                "url": f"/uploads/pictures/{test_file}"
            })
    
    return jsonify({
        "current_file": current_file,
        "current_directory": current_dir,
        "app_directory": app_dir,
        "working_directory": os.getcwd(),
        "recommended_path": working_path,
        "path_tests": results,
        "test_file_results": file_tests,
        "flask_routes_check": {
            "picture_route_exists": any('/uploads/pictures/' in str(rule) for rule in current_app.url_map.iter_rules())
        }
    })

@debug_bp.route('/picture-direct-test/<filename>')
def picture_direct_test(filename):
    """특정 파일 직접 접근 테스트"""
    
    # app/__init__.py에서 설정한 picture_path와 동일하게 계산
    app_dir = os.path.dirname(os.path.dirname(__file__))
    picture_path = os.path.abspath(os.path.join(app_dir, '../../database/picture'))
    
    file_path = os.path.join(picture_path, filename)
    
    return jsonify({
        "requested_filename": filename,
        "calculated_picture_path": picture_path,
        "full_file_path": file_path,
        "directory_exists": os.path.exists(picture_path),
        "file_exists": os.path.exists(file_path),
        "directory_contents": os.listdir(picture_path) if os.path.exists(picture_path) else [],
        "suggestion": f"브라우저에서 http://localhost:5000/uploads/pictures/{filename} 으로 접근해보세요"
    })