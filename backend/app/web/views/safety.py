# app/web/safety.py
from flask import Blueprint, jsonify, Response
import time
import json

from app import create_app
from app.util.auth import verify_token_from_query
from app.util.time_utils import get_korea_now_iso
from app.web.service import SafetyService

safety_bp = Blueprint('safety', __name__)

@safety_bp.route('/danger-employees/stream')
def danger_employees_stream():
    """
    위험 직원 실시간 스트림 API
    GET /api/web/safety/danger-employees/stream?token=JWT_TOKEN
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    # 앱 인스턴스 생성
    app = create_app()
    
    def generate_danger_stream():
        # 한국시간으로 초기 연결 메시지
        initial_message = {
            "status": "connected",
            "message": "위험 직원 데이터 스트림 연결 성공",
            "timestamp": get_korea_now_iso(),
            "risk_level": "위험"
        }
        yield f"data: {json.dumps(initial_message, ensure_ascii=False)}\n\n"
        time.sleep(1)
        
        while True:
            with app.app_context():
                try:
                    # 🔧 서비스 계층 사용
                    employees_data = SafetyService.get_employees_by_risk_level('위험')
                    
                    # 응답 데이터 생성
                    response_data = {
                        "timestamp": get_korea_now_iso(),
                        "status": "success",
                        "data": {
                            "risk_level": "위험",
                            "employees": employees_data,
                            "total_count": len(employees_data)
                        },
                        "meta": {
                            "timezone": "Asia/Seoul",
                            "last_updated": get_korea_now_iso()
                        }
                    }
                    
                    # SSE 형식으로 전송
                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                    
                except Exception as e:
                    error_data = {
                        "timestamp": get_korea_now_iso(),
                        "status": "error",
                        "message": "위험 직원 데이터 조회 중 오류가 발생했습니다.",
                        "details": str(e),
                        "risk_level": "위험"
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            # 5분 대기 (위험자는 더 자주 체크)
            time.sleep(300)
    
    return Response(
        generate_danger_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Content-Type': 'text/event-stream',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@safety_bp.route('/caution-employees/stream')
def caution_employees_stream():
    """
    주의 직원 실시간 스트림 API
    GET /api/web/safety/caution-employees/stream?token=JWT_TOKEN
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    # 앱 인스턴스 생성
    app = create_app()
    
    def generate_caution_stream():
        # 한국시간으로 초기 연결 메시지
        initial_message = {
            "status": "connected",
            "message": "주의 직원 데이터 스트림 연결 성공",
            "timestamp": get_korea_now_iso(),
            "risk_level": "주의"
        }
        yield f"data: {json.dumps(initial_message, ensure_ascii=False)}\n\n"
        time.sleep(1)
        
        while True:
            with app.app_context():
                try:
                    # 🔧 서비스 계층 사용
                    employees_data = SafetyService.get_employees_by_risk_level('주의')
                    
                    # 응답 데이터 생성
                    response_data = {
                        "timestamp": get_korea_now_iso(),
                        "status": "success",
                        "data": {
                            "risk_level": "주의",
                            "employees": employees_data,
                            "total_count": len(employees_data)
                        },
                        "meta": {
                            "timezone": "Asia/Seoul",
                            "last_updated": get_korea_now_iso()
                        }
                    }
                    
                    # SSE 형식으로 전송
                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                    
                except Exception as e:
                    error_data = {
                        "timestamp": get_korea_now_iso(),
                        "status": "error",
                        "message": "주의 직원 데이터 조회 중 오류가 발생했습니다.",
                        "details": str(e),
                        "risk_level": "주의"
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            # 5분 대기 (주의는 조금 덜 자주)
            time.sleep(300)
    
    return Response(
        generate_caution_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Content-Type': 'text/event-stream',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )