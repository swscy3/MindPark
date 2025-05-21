# app/web/__init__.py
from flask import Blueprint

# 디버그 및 유틸리티 모듈에서 블루프린트 import
from .debug import debug_bp
from .util import util_bp
from .auth import auth_bp

# 디버그 및 유틸리티 관련 블루프린트를 묶은 메인 블루프린트
utils_bp = Blueprint('utils', __name__)

# 하위 블루프린트들을 메인 블루프린트에 등록
# URL 접두사를 통해 각각의 역할 구분
utils_bp.register_blueprint(debug_bp, url_prefix='/debug')      # /api/utils/debug/*
utils_bp.register_blueprint(util_bp, url_prefix='/util')        # /api/utils/util/*
utils_bp.register_blueprint(auth_bp, url_prefix='/util')

# 전체 유틸리티 모듈을 하나의 블루프린트로 export
__all__ = ['utils_bp']