# app/web/employees.py
from flask import Blueprint, jsonify, Response
import time
import json

from app import create_app
from app.util.auth import verify_token_from_query
from app.util.time_utils import get_korea_today, get_korea_now_iso
from app.web.service import EmployeeService

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/list/stream')
def employees_list_stream():
    """
    전체 작업자 목록 실시간 스트림 API (Admin 제외)
    GET /api/web/emp/list/stream?token=JWT_TOKEN
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    # 앱 인스턴스 생성
    app = create_app()
    
    def generate_employees_stream():
        # 초기 연결 메시지
        yield "data: {\"status\":\"connected\",\"message\":\"작업자 목록 스트림 연결 성공\"}\n\n"
        time.sleep(1)
        
        while True:
            # 각 반복마다 새로운 앱 컨텍스트 생성
            with app.app_context():
                try:
                    # 서비스 계층 사용
                    korea_today = get_korea_today()
                    employees_data = EmployeeService.get_employee_list(korea_today)
                    
                    # 응답 데이터 생성
                    response_data = {
                        "timestamp": get_korea_now_iso(),
                        "korea_today": korea_today.isoformat(),
                        "status": "success",
                        "data": {
                            "employees": employees_data,
                            "total_count": len(employees_data)
                        }
                    }
                    
                    # SSE 형식으로 전송
                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                    
                except Exception as e:
                    error_data = {
                        "timestamp": get_korea_now_iso(),
                        "status": "error",
                        "message": "직원 목록 조회 중 오류가 발생했습니다.",
                        "details": str(e)
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            # 앱 컨텍스트 외부에서 sleep
            time.sleep(300)  # 5분 대기
    
    return Response(
        generate_employees_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Content-Type': 'text/event-stream',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )

@employees_bp.route('/<emp_id>/detail', methods=['GET'])
def get_employee_detail(emp_id):
    """
    작업자 상세정보 조회 API
    GET /api/web/emp/{emp_id}/detail?token=JWT_TOKEN
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    try:
        # 서비스 계층 사용
        korea_today = get_korea_today()
        employee_data = EmployeeService.get_employee_detail(emp_id, korea_today)
        
        if not employee_data:
            return jsonify({
                "timestamp": get_korea_now_iso(),
                "status": "error",
                "message": f"사번 {emp_id}인 직원을 찾을 수 없습니다."
            }), 404
        
        # 응답 데이터 생성
        response_data = {
            "timestamp": get_korea_now_iso(),
            "status": "success",
            "data": employee_data
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        return jsonify({
            "timestamp": get_korea_now_iso(),
            "status": "error",
            "message": "상세정보 조회 중 오류가 발생했습니다.",
            "details": str(e)
        }), 500