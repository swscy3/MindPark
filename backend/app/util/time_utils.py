# app/util/time_utils.py
"""
한국시간 관련 공용 유틸리티 함수들
"""
from datetime import datetime, date
import pytz

# 한국 시간대 설정
KST = pytz.timezone('Asia/Seoul')

def to_korea_time(dt):
    """
    UTC 시간을 한국 시간으로 변환
    
    Args:
        dt (datetime): UTC 시간 또는 naive datetime
        
    Returns:
        str: 한국시간 ISO 형식 문자열 또는 None
    """
    if dt is None:
        return None
    if dt.tzinfo is None:
        # naive datetime을 UTC로 가정하고 한국시간으로 변환
        dt = pytz.utc.localize(dt)
    return dt.astimezone(KST).isoformat()

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
    if utc_dt.tzinfo is None:
        utc_dt = pytz.utc.localize(utc_dt)
    korea_dt = utc_dt.astimezone(KST)
    return korea_dt.date()