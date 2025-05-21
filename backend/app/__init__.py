from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 확장 모듈 인스턴스 생성
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_name=None):
    # Flask 앱 생성
    app = Flask(__name__)
    
    # 설정 로드
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    from config import config
    app.config.from_object(config[config_name])
    
    # 확장 모듈 초기화
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    CORS(app)
    
    # 모델 임포트 (지연 임포트)
    from .model import Employee, Admin, EmployeeHealth, EmergencyContact, HealthAnomaly, Device, DeviceManagement, DeviceMeasurement, TokenBlocklist
    
    # JWT 설정
    print(f"JWT_SECRET_KEY 설정됨: {bool(app.config.get('JWT_SECRET_KEY'))}")
    
    # 토큰 블랙리스트 비우는 함수 정의
    def clear_token_blocklist():
        """앱 시작 시 토큰 블랙리스트 비우기"""
        try:
            # 토큰 블랙리스트 테이블의 모든 레코드 삭제
            count = TokenBlocklist.query.delete()
            db.session.commit()
            print(f"토큰 블랙리스트 초기화 완료: {count}개 토큰 삭제됨")
        except Exception as e:
            db.session.rollback()
            print(f"토큰 블랙리스트 초기화 실패: {str(e)}")
    
    # 앱 컨텍스트 내에서 블랙리스트 초기화 실행
    with app.app_context():
        clear_token_blocklist()
    
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None
    
    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        print(f"JWT 인증 실패: {callback}")
        return {"message": "토큰이 누락되었습니다"}, 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"message": "토큰이 만료되었습니다. 다시 로그인해주세요."}, 401
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"message": "유효하지 않은 토큰입니다."}, 401
    
    # 모바일 인증 블루프린트 등록
    from app.mobile.views import mobile_bp
    app.register_blueprint(mobile_bp, url_prefix='/api/mobile')
    
    # 공통 유틸 블루프린트 등록
    from app.util import utils_bp
    app.register_blueprint(utils_bp, url_prefix='/api')
    
    # 웹 유틸 일괄
    from app.web.views import web_bp
    app.register_blueprint(web_bp, url_prefix='/api/web')
    
    
    # 등록된 라우트 출력
    print("\n=== 등록된 라우트 목록 ===")
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f"{methods:10} {rule.rule:30} -> {rule.endpoint}")
    print("========================\n")
    
    # 기본 에러 핸들러
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'error': '요청한 리소스를 찾을 수 없습니다.'}), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500
    
    return app