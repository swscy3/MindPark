from flask import Flask, request, jsonify, send_from_directory
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
    CORS(app)  # CORS 허용 (개발 단계에서만)

    # 모델 임포트
    from .model import (
        Employee, Admin, EmployeeHealth, EmergencyContact, 
        HealthAnomaly, Device, DeviceManagement, 
        DeviceMeasurement, TokenBlocklist
    )

    # JWT 토큰 블랙리스트 초기화
    def clear_token_blocklist():
        try:
            count = TokenBlocklist.query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollback()

    with app.app_context():
        clear_token_blocklist()

    # JWT 관련 콜백
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None

    @jwt.unauthorized_loader
    def unauthorized_callback(callback):
        return {"message": "토큰이 누락되었습니다"}, 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return {"message": "토큰이 만료되었습니다. 다시 로그인해주세요."}, 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return {"message": "유효하지 않은 토큰입니다."}, 401

    # === 프로필 사진 정적 파일 서빙 === 
    picture_path = '/root/MindPark/database/picture'

    @app.route('/uploads/pictures/<filename>')
    def uploaded_pictures(filename):
        """프로필 사진 서빙 (확장자 자동 매칭)"""
        original_filename = filename
        
        # 확장자가 없는 경우 자동으로 찾기
        if not os.path.splitext(filename)[1]:  # 확장자가 없으면
            possible_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
            
            for ext in possible_extensions:
                test_filename = filename + ext
                test_path = os.path.join(picture_path, test_filename)
                
                if os.path.exists(test_path):
                    filename = test_filename
                    break
        
        try:
            return send_from_directory(picture_path, filename)
        except FileNotFoundError:
            return jsonify({'error': f'이미지를 찾을 수 없습니다: {original_filename}'}), 404
        except Exception as e:
            return jsonify({'error': f'이미지 로드 실패: {str(e)}'}), 500

    # 블루프린트 등록
    from app.mobile.views import mobile_bp
    app.register_blueprint(mobile_bp, url_prefix='/api/mobile')

    from app.util import utils_bp
    app.register_blueprint(utils_bp, url_prefix='/api')

    from app.web.views import web_bp
    app.register_blueprint(web_bp, url_prefix='/api/web')

    # 정적 Vue 파일 경로 (빌드된 파일이 있는 위치)
    vue_dist_path = os.path.join(os.path.dirname(__file__),  '../../frontend/dist')

    # Vue 정적 파일 서빙 라우트
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_vue(path):
        target_path = os.path.join(vue_dist_path, path)
        if path != "" and os.path.exists(target_path):
            return send_from_directory(vue_dist_path, path)
        else:
            return send_from_directory(vue_dist_path, 'index.html')

    # 에러 핸들러
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'error': '요청한 리소스를 찾을 수 없습니다.'}), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return jsonify({'error': '서버 내부 오류가 발생했습니다.'}), 500

    return app