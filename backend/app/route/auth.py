from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, create_access_token
from app import db
from app.models.employee import Employee, Admin
from app.models.token import TokenBlocklist
from app.schemas.auth import LoginSchema
from marshmallow import ValidationError
from datetime import datetime, timezone

app_auth_bp = Blueprint('app_auth', __name__)

@app_auth_bp.route('/app/login', methods=['POST'])
def app_login():
    """
    앱 로그인 API
    
    로직:
    1. 로그인 시도
    2. Employee.emp_id에 일치하는 아이디 있나 확인
       2-1. 있다 : 진행
       2-2. 없다 : 로그인 불허 
    3. Admin.admin_id에 일치하는 아이디 있나 확인
       3-1. 있다 : 로그인 불허 "관리자는 web only세요"
       3-2. 없다 : 로그인 완료
    """
    
    # 스키마를 사용하여 요청 데이터 검증
    schema = LoginSchema()
    try:
        data = schema.load(request.json)
    except ValidationError as err:
        return jsonify({"error": "유효하지 않은 입력입니다", "details": err.messages}), 400
    
    # 1. 사용자 확인 (Employee.emp_id에 일치하는 아이디 있나 확인)
    user = Employee.query.filter_by(emp_id=data['id']).first()
    
    # 2-2. 사용자가 없거나 비밀번호가 일치하지 않는 경우 로그인 불허
    if not user or not user.check_password(data['password']):
        return jsonify({"error": "아이디 또는 비밀번호가 잘못되었습니다"}), 401
    
    # 3. Admin.admin_id에 일치하는 아이디 있나 확인
    admin = Admin.query.filter_by(admin_id=data['id']).first()
    
    # 3-1. 관리자인 경우 로그인 불허
    if admin:
        return jsonify({"error": "관리자는 웹에서만 로그인할 수 있습니다"}), 403
    
    # 3-2. 관리자가 아닌 일반 직원인 경우 로그인 완료
    access_token = create_access_token(identity=user.emp_id)
    
    return jsonify({
        "message": "로그인 성공",
        "token": access_token
    }), 200

@app_auth_bp.route('/app/logout', methods=['POST'])
@jwt_required()
def app_logout():
    """
    앱 로그아웃 API
    """
    # 현재 JWT 토큰 정보 가져오기
    jwt_data = get_jwt()
    jti = jwt_data["jti"]  # JWT ID
    now = datetime.now(timezone.utc)
    
    # 토큰 만료 시간 계산
    expires = datetime.fromtimestamp(jwt_data["exp"], timezone.utc)
    
    # 토큰을 블랙리스트에 추가
    db.session.add(TokenBlocklist(jti=jti, created_at=now, expires_at=expires))
    db.session.commit()
    
    return jsonify({"message": "앱 로그아웃 성공"}), 200