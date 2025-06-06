# app/web/__init__.py
from flask import Blueprint

# 각 모듈에서 블루프린트 import
from .auth import web_auth_bp
from .alert import alert_bp
from .monitoring import monitoring_bp
from .safety import safety_bp
from .employees import employees_bp

# 웹 관련 모든 블루프린트를 묶은 메인 블루프린트
web_bp = Blueprint('web_main', __name__)

# 하위 블루프린트들을 메인 블루프린트에 등록
# URL 접두사를 통해 각각의 역할 구분
web_bp.register_blueprint(web_auth_bp, url_prefix='/auth')       # /api/web/auth/*
web_bp.register_blueprint(alert_bp, url_prefix='/alert')
web_bp.register_blueprint(monitoring_bp,url_prefix='/monitoring')
web_bp.register_blueprint(safety_bp,url_prefix='/safety')
web_bp.register_blueprint(employees_bp,url_prefix='/emp')

# 전체 웹 모듈을 하나의 블루프린트로 export
__all__ = ['web_bp']