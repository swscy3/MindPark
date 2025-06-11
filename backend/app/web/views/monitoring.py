# app/web/monitoring.py
from flask import Blueprint, Response, jsonify
import time
import json

from app import create_app
from app.util.auth import verify_token_from_query
from app.util.time_utils import get_korea_today, get_korea_now_iso
from app.web.service import MonitoringService

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/dashboard/stream')
def dashboard_stream():
    """
    대시보드 모니터링 스트림 API
    GET /api/web/monitoring/dashboard/stream?token=JWT_TOKEN
    """
    # 토큰 검증
    is_valid, result = verify_token_from_query()
    if not is_valid:
        return jsonify({"error": result}), 401
    
    app = create_app()
    
    def generate_dashboard_stream():
        # 한국시간으로 연결 메시지 타임스탬프 수정
        initial_message = {
            "status": "connected",
            "message": "대시보드 모니터링 스트림 연결 성공",
            "timestamp": get_korea_now_iso()
        }
        yield f"data: {json.dumps(initial_message, ensure_ascii=False)}\n\n"
        time.sleep(1)
        
        while True:
            with app.app_context():
                try:
                    # 🔧 서비스 계층 사용
                    korea_today = get_korea_today()
                    dashboard_data = MonitoringService.get_dashboard_data(korea_today)
                    
                    # 응답 데이터 생성
                    current_time = get_korea_now_iso()
                    
                    response_data = {
                        "timestamp": current_time,
                        "status": "success",
                        "data": {
                            "heat_risk_employees": dashboard_data["heat_risk_employees"],
                            "fall_risk_employees": dashboard_data["fall_risk_employees"],
                            "device_status": {
                                **dashboard_data["device_status"],
                                "last_updated": current_time
                            }
                        },
                        "debug_info": {
                            "heat_risk_count": len(dashboard_data["heat_risk_employees"]),
                            "fall_risk_count": len(dashboard_data["fall_risk_employees"]),
                            "timezone": "Asia/Seoul",
                            "korea_today": korea_today.isoformat()
                        }
                    }

                    yield f"data: {json.dumps(response_data, ensure_ascii=False)}\n\n"
                    
                except Exception as e:
                    error_data = {
                        "timestamp": get_korea_now_iso(),
                        "status": "error", 
                        "message": "대시보드 데이터 조회 중 오류가 발생했습니다.",
                        "details": str(e)
                    }
                    yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
            
            time.sleep(300)  # 5분 대기
    
    return Response(
        generate_dashboard_stream(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache, no-transform',
            'Content-Type': 'text/event-stream',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive',
            'Access-Control-Allow-Origin': '*'
        }
    )