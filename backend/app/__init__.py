from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

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
    
    # 블루프린트 등록
    from app.routes.auth import auth_bp
    from app.routes.employee import employee_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.device import device_bp
    from app.routes.health import health_bp
    from app.routes.anomaly import anomaly_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(employee_bp, url_prefix='/api')
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(device_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(anomaly_bp, url_prefix='/api')
    
    # 에러 핸들러 등록
    @app.errorhandler(404)
    def page_not_found(e):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return {'error': 'Internal server error'}, 500
    
    # Shell 컨텍스트 설정
    @app.shell_context_processor
    def make_shell_context():
        # 모델 가져오기
        from app.models.employee import Employee, Admin
        from app.models.health import EmployeeHealth, EmergencyContact, HealthAnomaly
        from app.models.device import Device, DeviceManagement, DeviceFailure
        from app.models.measurement import DeviceMeasurement
        
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
            DeviceMeasurement=DeviceMeasurement
        )
    
    return app