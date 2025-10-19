# app/api/auth.py (공통 API 라우트)
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from app.model import Employee, db
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    비밀번호 변경 API (웹/앱 공용)
    
    POST /api/auth/change-password
    {
        "current_password": "현재 비밀번호",
        "new_password": "새 비밀번호"
    }
    """
    # JWT에서 사용자 ID 가져오기
    current_user_id = get_jwt_identity()
    
    # 요청 데이터 확인
    data = request.get_json()
    if not data or 'current_password' not in data or 'new_password' not in data:
        return jsonify({"error": "현재 비밀번호와 새 비밀번호를 모두 입력해주세요"}), 400
    
    current_password = data['current_password']
    new_password = data['new_password']
    
    # 비밀번호 검증
    if len(new_password) < 6:
        return jsonify({"error": "비밀번호는 최소 6자 이상이어야 합니다"}), 400
    
    # 사용자 조회
    employee = Employee.query.filter_by(emp_id=current_user_id).first()
    if not employee:
        return jsonify({"error": "사용자를 찾을 수 없습니다"}), 404
    
    # 현재 비밀번호 확인
    if not employee.check_password(current_password):
        return jsonify({"error": "현재 비밀번호가 일치하지 않습니다"}), 401
    
    # 비밀번호 변경
    employee.password = new_password
    db.session.commit()
    
    return jsonify({"message": "비밀번호가 성공적으로 변경되었습니다"}), 200


def verify_token_from_query():
    """쿼리 파라미터에서 토큰을 검증하는 함수"""
    token = request.args.get('token')
    if not token:
        return False, "토큰이 필요합니다"
    
    try:
        # 토큰 디코드 및 검증
        decoded_token = decode_token(token)
        
        # 토큰 만료 확인
        exp = decoded_token.get('exp')
        if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
            return False, "토큰이 만료되었습니다"
            
        return True, decoded_token
    except Exception as e:
        return False, f"유효하지 않은 토큰입니다: {str(e)}"


def verify_token_from_header():
    """Authorization 헤더에서 토큰을 검증하는 함수 (향후 확장용)"""
    # 필요시 구현
    pass