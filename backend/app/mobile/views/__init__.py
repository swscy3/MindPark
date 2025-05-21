# 모바일 블루프린트 통합 파일
from flask import Blueprint

# 모바일 메인 블루프린트 생성
mobile_bp = Blueprint('mobile', __name__)

# 모바일 서브 블루프린트 가져오기
from .auth import mobile_auth_bp
from .profile import mobile_profile_bp
from .device import device_bp

# 모바일 서브 블루프린트 등록
mobile_bp.register_blueprint(mobile_auth_bp, url_prefix='/auth')
mobile_bp.register_blueprint(mobile_profile_bp, url_prefix='/profile')
mobile_bp.register_blueprint(device_bp, url_prefix='/device')

__all__ = ['mobile_bp']