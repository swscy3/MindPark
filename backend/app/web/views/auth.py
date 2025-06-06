# app/web/auth.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timezone
from marshmallow import ValidationError
import os
from app.schema import LoginSchema
from app.model import Employee, Admin, db, TokenBlocklist
from ..service import AuthService

web_auth_bp = Blueprint('web_auth', __name__)


@web_auth_bp.route('/login', methods=['POST'])
def web_login():
    """
    웹 로그인 API (관리자 전용)
    POST /api/web/login
    """
    try:
        # 1. 입력 데이터 검증
        schema = LoginSchema()
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({
            "error": "유효하지 않은 입력입니다",
            "details": err.messages
        }), 400
    
    # 2. 서비스를 통한 인증 처리
    admin, error_message = AuthService.verify_admin_credentials(
        data['id'], data['password']
    )
    
    if error_message:
        if "권한" in error_message:
            return jsonify({"error": error_message}), 403
        else:
            return jsonify({"error": error_message}), 401
    
    # 3. 직원 정보 조회 (이름, 사진 가져오기)
    employee = Employee.query.filter_by(emp_id=admin.admin_id).first()
    
    # 4. 사진 경로를 웹 URL로 변환
    picture_url = None
    if employee and employee.picture:
        # /root/MindPark/database/picture/woman8 -> woman8
        filename = os.path.basename(employee.picture)
        # /uploads/pictures/woman8 형태로 변환
        picture_url = f"/uploads/pictures/{filename}"
    
    # 5. JWT 토큰 생성
    access_token = create_access_token(identity=data['id'])
    
    return jsonify({
        "message": "로그인 성공",
        "token": access_token,
        "admin": {
            "id": admin.admin_id,
            "name": employee.name if employee else "",
            "picture": picture_url  # 웹에서 바로 쓸 수 있는 URL
        }
    }), 200

@web_auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def web_logout():
    """
    웹 로그아웃 API
    POST /api/web/auth/logout
    """
    try:
        # 현재 JWT 토큰 정보 가져오기
        jwt_data = get_jwt()
        jti = jwt_data['jti']  # JWT ID
        exp = jwt_data['exp']  # 만료 시간 (Unix timestamp)
        
        # 토큰을 블랙리스트에 추가
        blocked_token = TokenBlocklist(
            jti=jti,
            created_at=datetime.now(timezone.utc),
            expires_at=datetime.fromtimestamp(exp, tz=timezone.utc)
        )
        
        db.session.add(blocked_token)
        db.session.commit()
        
        return jsonify({"message": "로그아웃 성공"}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"로그아웃 처리 중 오류가 발생했습니다: {str(e)}"}), 500