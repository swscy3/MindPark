from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..service.profile_service import ProfileService

# 모바일 프로필 블루프린트 생성
mobile_profile_bp = Blueprint('mobile_profile', __name__)

@mobile_profile_bp.route('/mypage', methods=['PUT', 'POST'])
@jwt_required()
def update_mypage():
    """
    마이페이지 정보 수정 - 업데이트 후 최신 데이터 반환
    
    PUT/POST /api/mobile/profile/mypage
    {
        "phone": "010-1234-5678",
        "HT": true,
        "HeartDisease": false,
        "other_conditions": "알레르기",
        "guardian_name": "홍길동",
        "guardian_rel": "배우자",
        "guardian_phone": "010-9876-5432"
    }
    """
    try:
        # JWT에서 사번 추출
        emp_id = get_jwt_identity()
        
        # 요청 데이터 가져오기
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400
        
        # 서비스 레이어 호출
        success, message = ProfileService.update_profile(emp_id, data)
        
        if not success:
            return jsonify({"error": message}), 400
        
        # 업데이트 성공 시 최신 데이터 조회
        updated_data = ProfileService.get_profile(emp_id)
        
        return jsonify({
            "message": message,
            "data": updated_data
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"서버 오류가 발생했습니다: {str(e)}"}), 500

@mobile_profile_bp.route('/mypage', methods=['GET'])
@jwt_required()
def get_mypage():
    """
    마이페이지 정보 조회
    
    GET /api/mobile/profile/mypage
    """
    try:
        emp_id = get_jwt_identity()
        
        profile_data = ProfileService.get_profile(emp_id)
        
        if not profile_data:
            return jsonify({"error": "프로필 정보를 찾을 수 없습니다"}), 404
            
        return jsonify({"data": profile_data}), 200
        
    except Exception as e:
        return jsonify({"error": f"서버 오류가 발생했습니다: {str(e)}"}), 500