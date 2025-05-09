from app import db
from app.models.token import TokenBlocklist
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)

def add_token_to_blocklist(jti, expires_at):
    """
    JWT 토큰을 블랙리스트에 추가하는 함수
    
    Args:
        jti (str): JWT 토큰의 고유 ID
        expires_at (datetime): 토큰 만료 시간
    
    Returns:
        bool: 블랙리스트에 추가 성공 여부
    """
    try:
        token = TokenBlocklist(
            jti=jti,
            created_at=datetime.now(timezone.utc),
            expires_at=expires_at
        )
        db.session.add(token)
        db.session.commit()
        return True
    except Exception as e:
        logger.error(f"토큰 블랙리스트 추가 실패: {str(e)}")
        db.session.rollback()
        return False

def is_token_revoked(jti):
    """
    JWT 토큰이 블랙리스트에 있는지 확인하는 함수
    
    Args:
        jti (str): JWT 토큰의 고유 ID
    
    Returns:
        bool: 토큰이 블랙리스트에 있으면 True, 아니면 False
    """
    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None

def clean_token_blocklist():
    """
    만료된 토큰을 블랙리스트에서 제거하는 함수
    
    이 함수는 주기적으로 실행하여 데이터베이스 크기를 관리할 수 있습니다.
    예: 스케줄러에서 매일 자정에 실행
    
    Returns:
        int: 제거된 토큰 수
    """
    try:
        now = datetime.now(timezone.utc)
        expired_tokens = TokenBlocklist.query.filter(TokenBlocklist.expires_at < now).all()
        
        count = len(expired_tokens)
        if count > 0:
            for token in expired_tokens:
                db.session.delete(token)
            
            db.session.commit()
            logger.info(f"{count}개의 만료된 토큰을 블랙리스트에서 제거했습니다.")
        
        return count
    except Exception as e:
        logger.error(f"블랙리스트 정리 실패: {str(e)}")
        db.session.rollback()
        return 0

def get_active_blocklist_count():
    """
    현재 활성 상태인(아직 만료되지 않은) 블랙리스트 토큰 수를 반환하는 함수
    
    Returns:
        int: 활성 상태인 블랙리스트 토큰 수
    """
    now = datetime.now(timezone.utc)
    return TokenBlocklist.query.filter(TokenBlocklist.expires_at >= now).count()