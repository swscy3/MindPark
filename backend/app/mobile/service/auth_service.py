# app/service/auth_service.py
from flask_jwt_extended import create_access_token
from datetime import datetime, timezone
from app.model import Employee, Admin, EmployeeHealth, EmergencyContact, TokenBlocklist, db

class AuthService:
    @staticmethod
    def login(emp_id, password):
        # 직원 조회
        employee = Employee.query.filter_by(emp_id=emp_id).first()
        if not employee:
            return None, "아이디 또는 비밀번호가 잘못되었습니다"
        
        # 비밀번호 확인
        if not employee.check_password(password):
            return None, "아이디 또는 비밀번호가 잘못되었습니다"
        
        # 관리자 여부 확인
        admin = Admin.query.filter_by(admin_id=emp_id).first()
        if admin:
            return None, "관리자는 웹에서만 로그인할 수 있습니다"
        
        # JWT 토큰 생성
        access_token = create_access_token(identity=emp_id)
        
        return access_token, None
    
    @staticmethod
    def logout(jwt_payload):
        """
        토큰 블랙리스트에 추가하여 로그아웃 처리
        
        Args:
            jwt_payload: JWT 페이로드
            
        Returns:
            bool: 로그아웃 성공 여부
        """
        jti = jwt_payload["jti"]
        now = datetime.now(timezone.utc)
        expires = datetime.fromtimestamp(jwt_payload["exp"], timezone.utc)
        
        # 토큰 블랙리스트에 추가
        token_block = TokenBlocklist(
            jti=jti,
            created_at=now,
            expires_at=expires
        )
        
        try:
            db.session.add(token_block)
            db.session.commit()
            return True
        except Exception:
            db.session.rollback()
            return False
    
    @staticmethod
    def get_user_profile(emp_id):
        """
        사용자 프로필 정보 조회

        Args:
            emp_id (str): 직원 ID
        
        Returns:
            tuple: (사용자 데이터, 에러 메시지)
        """
        # 직원 기본 정보
        employee = Employee.query.filter_by(emp_id=emp_id).first()
        if not employee:
            return None, "직원 정보를 찾을 수 없습니다"
    
        # 건강 정보 조회
        health_info = EmployeeHealth.query.filter_by(emp_id=emp_id).first()
        emergency_contact = EmergencyContact.query.filter_by(emp_id=emp_id).first()
    
        # 기저질환 여부 확인
        diseases = []
    
        if health_info:
            disease_mapping = {
                'HT': '고혈압',
                'HeartDisease': '심장질환', 
                'Pscyco': '정신질환',
                'DM': '당뇨병',
                'CerevD': '뇌혈관질환',
                'CKD': '만성신장질환'
            }
        
            for field, disease_name in disease_mapping.items():
                if getattr(health_info, field, False):
                    diseases.append(disease_name)
    
        # 사용자 정보 반환
        user_data = {
            "empId": employee.emp_id,
            "name": employee.name,
            "age": str(employee.age),
            "diseases": diseases,
            "otherConditions": health_info.other_conditions if health_info else "",
            "guardianName": emergency_contact.contact_name if emergency_contact else "",
            "guardianRelation": emergency_contact.relation if emergency_contact else "",
            "guardianPhone": emergency_contact.contact_phone if emergency_contact else ""
        }
    
        return user_data, None