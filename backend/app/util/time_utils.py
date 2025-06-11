"""
한국시간 관련 공용 유틸리티 함수들
"""
from datetime import datetime, date
import pytz

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')
UTC = pytz.timezone('UTC')

def to_korea_time(dt):
    """
    UTC 시간을 한국 시간으로 변환 (ISO 형식)
    
    Args:
        dt (datetime): UTC 시간 또는 naive datetime
        
    Returns:
        str: 한국시간 ISO 형식 문자열 또는 None
    """
    if dt is None:
        return None
    
    try:
        if dt.tzinfo is None:
            # naive datetime을 UTC로 가정하고 한국시간으로 변환
            dt = UTC.localize(dt)
        
        # 한국시간으로 변환 후 ISO 형식으로 반환
        korea_dt = dt.astimezone(KST)
        return korea_dt.isoformat()
        
    except Exception as e:
        print(f"[ERROR] 시간 변환 오류: {str(e)}, 입력값: {dt}")
        return None

def to_korea_time_formatted(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """
    UTC 시간을 한국 시간으로 변환 (사용자 정의 형식)
    
    Args:
        dt (datetime): UTC 시간 또는 naive datetime
        format_str (str): 출력 형식 (기본값: "%Y-%m-%d %H:%M:%S")
        
    Returns:
        str: 한국시간 포맷된 문자열 또는 None
    """
    if dt is None:
        return None
    
    try:
        if dt.tzinfo is None:
            # naive datetime을 UTC로 가정하고 한국시간으로 변환
            dt = UTC.localize(dt)
        
        # 한국시간으로 변환 후 지정된 형식으로 반환
        korea_dt = dt.astimezone(KST)
        return korea_dt.strftime(format_str)
        
    except Exception as e:
        print(f"[ERROR] 시간 변환 오류: {str(e)}, 입력값: {dt}")
        return None

def get_korea_now():
    """
    현재 한국 시간을 문자열로 반환
    
    Returns:
        str: 현재 한국시간 (YYYY-MM-DD HH:MM:SS 형식)
    """
    return datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")

def get_korea_now_iso():
    """
    현재 한국 시간을 ISO 형식으로 반환
    
    Returns:
        str: 현재 한국시간 ISO 형식
    """
    return datetime.now(KST).isoformat()

def get_korea_today():
    """
    한국 시간 기준 오늘 날짜 반환
    
    Returns:
        date: 한국시간 기준 오늘 날짜
    """
    korea_now = datetime.now(KST)
    return korea_now.date()

def get_korea_datetime():
    """
    현재 한국 시간 datetime 객체 반환
    
    Returns:
        datetime: 한국시간 datetime 객체 (timezone 정보 포함)
    """
    return datetime.now(KST)

def utc_to_korea_date(utc_dt):
    """
    UTC datetime을 한국시간 date로 변환
    
    Args:
        utc_dt (datetime): UTC datetime
        
    Returns:
        date: 한국시간 기준 날짜
    """
    if utc_dt is None:
        return None
    
    try:
        if utc_dt.tzinfo is None:
            utc_dt = UTC.localize(utc_dt)
        korea_dt = utc_dt.astimezone(KST)
        return korea_dt.date()
    except Exception as e:
        print(f"[ERROR] 날짜 변환 오류: {str(e)}, 입력값: {utc_dt}")
        return None

def korea_to_utc(korea_dt_str):
    """
    한국시간 문자열을 UTC datetime으로 변환
    
    Args:
        korea_dt_str (str): 한국시간 문자열 (ISO 형식 또는 "YYYY-MM-DD HH:MM:SS" 형식)
        
    Returns:
        datetime: UTC datetime 객체 또는 None
    """
    if not korea_dt_str:
        return None
    
    try:
        # ISO 형식 시도
        try:
            korea_dt = datetime.fromisoformat(korea_dt_str.replace('Z', '+00:00'))
            if korea_dt.tzinfo is None:
                korea_dt = KST.localize(korea_dt)
        except:
            # 일반 형식 시도
            korea_dt = datetime.strptime(korea_dt_str, "%Y-%m-%d %H:%M:%S")
            korea_dt = KST.localize(korea_dt)
        
        return korea_dt.astimezone(UTC)
        
    except Exception as e:
        print(f"[ERROR] UTC 변환 오류: {str(e)}, 입력값: {korea_dt_str}")
        return None

def validate_datetime_field(dt):
    """
    datetime 필드 유효성 검사 및 디버깅 정보 출력
    
    Args:
        dt (datetime): 검사할 datetime 객체
        
    Returns:
        dict: 검사 결과 정보
    """
    if dt is None:
        return {
            'valid': False,
            'type': 'None',
            'timezone': None,
            'korea_time': None
        }
    
    result = {
        'valid': True,
        'type': type(dt).__name__,
        'timezone': str(dt.tzinfo) if dt.tzinfo else 'naive',
        'original_value': str(dt),
        'korea_time': to_korea_time(dt)
    }
    
    return result

# 디버깅용 함수
def debug_time_conversion(dt, field_name=""):
    """
    시간 변환 디버깅 정보 출력
    
    Args:
        dt (datetime): 디버깅할 datetime 객체
        field_name (str): 필드명 (로그용)
    """
    validation_result = validate_datetime_field(dt)
    print(f"[DEBUG] {field_name} 시간 변환 정보:")
    print(f"  - 유효성: {validation_result['valid']}")
    print(f"  - 타입: {validation_result['type']}")
    print(f"  - 시간대: {validation_result['timezone']}")
    print(f"  - 원본값: {validation_result.get('original_value', 'None')}")
    print(f"  - 한국시간: {validation_result['korea_time']}")
    print("-" * 50)