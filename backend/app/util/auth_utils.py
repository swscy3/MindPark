# app/utils/auth_utils.py
from flask import request
from flask_jwt_extended import decode_token
from datetime import datetime, timezone

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