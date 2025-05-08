from app import db
from datetime import datetime

class TokenBlocklist(db.Model):
    """
    JWT 토큰 블랙리스트를 저장하는 모델
    
    이 모델은 로그아웃된 JWT 토큰을 추적하여 해당 토큰이
    더 이상 API에 접근하지 못하도록 합니다.
    """
    __tablename__ = 'TOKEN_BLOCKLIST'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<TokenBlocklist {self.jti}>'