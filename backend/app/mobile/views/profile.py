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
        "Pscyco": true,
        "DM": false,
        "CerevD": false,
        "CKD": true,
        "otherConditions": "알레르기",
        "guardianName": "홍길동",
        "guardianRelation": "배우자",
        "guardianPhone": "010-9876-5432"
    }
    """
    try:
        # JWT에서 사번 추출
        emp_id = get_jwt_identity()
        
        # 요청 데이터 가져오기
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "요청 데이터가 없습니다"}), 400
        
        # 카멜케이스 -> 스네이크케이스 변환 (서비스 레이어 호출용)
        converted_data = {}
        
        # 기본 정보
        if 'phone' in data:
            converted_data['phone'] = data['phone']
            
        # 질병 정보 (이미 올바른 필드명)
        disease_fields = ['HT', 'HeartDisease', 'Pscyco', 'DM', 'CerevD', 'CKD']
        for field in disease_fields:
            if field in data:
                converted_data[field] = data[field]
                
        if 'otherConditions' in data:
            converted_data['other_conditions'] = data['otherConditions']
            
        # 보호자 정보
        if 'guardianName' in data:
            converted_data['guardian_name'] = data['guardianName']
        if 'guardianRelation' in data:
            converted_data['guardian_rel'] = data['guardianRelation']  
        if 'guardianPhone' in data:
            converted_data['guardian_phone'] = data['guardianPhone']
        
        # 서비스 레이어 호출
        success, message = ProfileService.update_profile(emp_id, converted_data)
        
        if not success:
            return jsonify({"error": message}), 400
        
        # 업데이트 성공 시 최신 데이터 조회 (카멜케이스로 응답)
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
    
    응답 예시:
    {
        "data": {
            "empId": "EN0003",
            "name": "박서윤",
            "age": "41",
            "diseases": ["심장질환", "정신질환", "당뇨병", "만성신장질환"],
            "otherConditions": null,
            "guardianName": "신예은",
            "guardianPhone": "010-8008-9128",
            "guardianRelation": "부"
        }
    }
    """
    try:
        emp_id = get_jwt_identity()
        
        profile_data = ProfileService.get_profile(emp_id)
        
        if not profile_data:
            return jsonify({"error": "프로필 정보를 찾을 수 없습니다"}), 404
            
        return jsonify({"data": profile_data}), 200
        
    except Exception as e:
        return jsonify({"error": f"서버 오류가 발생했습니다: {str(e)}"}), 500