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
