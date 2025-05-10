from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
import logging  # 추가
from logging.handlers import RotatingFileHandler  # 추가
from dotenv import load_dotenv
# .env 파일 로드 (개발 환경용)
load_dotenv()

# 데이터베이스 및 확장 모듈 인스턴스 생성
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name=None):
    # Flask 앱 인스턴스 생성
    app = Flask(__name__)
    
    # 설정 로드
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # 데이터베이스 및 확장 모듈 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # 로깅 설정 추가 (여기에 새 코드 추가)
    if not app.debug and not app.testing:
        # 로그 디렉토리 생성
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # 로그 파일 핸들러 설정 (텍스트 파일로 저장)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'app.txt'),  # .txt 확장자 사용
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5  # 최대 5개 백업 파일
        )
        
        # 로그 포맷 설정
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # 로그 레벨 설정 - 이 부분이 변경됨
        log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
        file_handler.setLevel(log_level)
        
        # 앱 로거에 핸들러 추가
        app.logger.addHandler(file_handler)
        app.logger.setLevel(log_level)
        
        # 로깅 시작 메시지
        app.logger.info(f"{'='*20} 애플리케이션 시작 {'='*20}")
        app.logger.info(f"실행 환경: {config_name}")
    
    # JWT 토큰 블랙리스트 확인 콜백 설정
    from models.token import TokenBlocklist
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None
    
    # 토큰 만료 처리
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"message": "토큰이 만료되었습니다. 다시 로그인해주세요."}, 401
    
    # 유효하지 않은 토큰 처리
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"message": "유효하지 않은 토큰입니다."}, 401
    
    # 블루프린트 등록
    from route.auth import auth_bp
    from route.employee import employee_bp
    from route.dashboard import dashboard_bp
    from route.device import device_bp
    from route.health import health_bp
    from route.anomaly import anomaly_bp
    from route_mobile.auth import mobile_auth_bp
    from route_mobile.dashboard import app_dashboard_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(employee_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(device_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(anomaly_bp, url_prefix='/api')
    app.register_blueprint(mobile_auth_bp, url_prefix='/api')
    app.register_blueprint(app_dashboard_bp,url_prefix='/api')
    
    # 에러 핸들러 등록
    @app.errorhandler(404)
    def page_not_found(e):
        if app.logger.isEnabledFor(logging.WARNING):
            app.logger.warning(f"404 오류: {request.path}")
        return {'error': '요청한 리소스를 찾을 수 없습니다.'}, 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"500 서버 오류: {str(e)}")
        return {'error': '서버 내부 오류가 발생했습니다.'}, 500
    
    # Shell 컨텍스트 설정
    @app.shell_context_processor
    def make_shell_context():
        # 모델 가져오기
        from app.models.employee import Employee, Admin
        from app.models.health import EmployeeHealth, EmergencyContact, HealthAnomaly
        from app.models.device import Device, DeviceManagement, DeviceFailure
        from app.models.measurement import DeviceMeasurement
        from app.models.token import TokenBlocklist
        
        return dict(
            db=db, 
            Employee=Employee, 
            Admin=Admin,
            EmployeeHealth=EmployeeHealth,
            EmergencyContact=EmergencyContact,
            HealthAnomaly=HealthAnomaly,
            Device=Device,
            DeviceManagement=DeviceManagement,
            DeviceFailure=DeviceFailure,
            DeviceMeasurement=DeviceMeasurement,
            TokenBlocklist=TokenBlocklist
        )
        
    app.logger.info("애플리케이션이 성공적으로 초기화되었습니다.")
    app.logger.warning("이것은 경고 로그 테스트입니다.")
    app.logger.error("이것은 오류 로그 테스트입니다.")
    
    return app

