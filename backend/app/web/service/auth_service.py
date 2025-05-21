# app/service/auth_service.py (또는 다른 위치에 있는 verify 메서드들)
from app.model import Employee, Admin, db

class AuthService:
    @staticmethod
    def verify_employee_credentials(emp_id, password):
        """
        직원 인증을 처리하는 메서드
        
        Args:
            emp_id (str): 직원 ID
            password (str): 비밀번호
            
        Returns:
            tuple: (직원 객체 또는 None, 오류 메시지 또는 None)
        """
        # 1. 직원 ID로 직원 정보 조회
        employee = Employee.query.filter_by(emp_id=emp_id).first()
        
        # 2. 직원이 존재하지 않는 경우
        if not employee:
            return None, "존재하지 않는 직원 ID입니다"
        
        # 디버깅 로그
        print(f"인증 시도: {emp_id}")
        print(f"저장된 비밀번호: '{employee.password}'")
        print(f"입력된 비밀번호: '{password}'")
        
        # 3. 비밀번호 확인
        # 저장된 비밀번호가 있는 경우
        if employee.password:
            if str(employee.password) != str(password):
                return None, "비밀번호가 일치하지 않습니다"
        else:
            # 저장된 비밀번호가 없는 경우 생년월일 확인
            if not employee.birth:
                return None, "생년월일이 설정되지 않았습니다"
                
            birth_password = employee.birth.strftime('%Y%m%d')
            if birth_password != str(password):
                return None, "비밀번호가 일치하지 않습니다"
                
            # 로그인 성공 시 비밀번호 필드에 생년월일 저장 (자동 마이그레이션)
            employee.password = birth_password
            db.session.commit()
        
        return employee, None
    
    @staticmethod
    def verify_admin_credentials(admin_id, password):
        """
        관리자 인증을 처리하는 메서드
        
        Args:
            admin_id (str): 관리자 ID
            password (str): 비밀번호
            
        Returns:
            tuple: (관리자 객체 또는 None, 오류 메시지 또는 None)
        """
        # 1. 직원 ID로 직원 정보 조회 (관리자는 직원이기도 함)
        employee = Employee.query.filter_by(emp_id=admin_id).first()
        
        # 2. 직원이 존재하지 않는 경우
        if not employee:
            return None, "존재하지 않는 ID입니다"
        
        # 디버깅 로그
        print(f"관리자 인증 시도: {admin_id}")
        print(f"저장된 비밀번호: '{employee.password}'")
        print(f"입력된 비밀번호: '{password}'")
        
        # 3. 비밀번호 확인
        if employee.password:
            # 저장된 비밀번호가 있는 경우 - 문자열로 변환하여 비교
            if str(employee.password) != str(password):
                return None, "비밀번호가 일치하지 않습니다"
        else:
            # 저장된 비밀번호가 없는 경우 생년월일 확인
            if not employee.birth:
                return None, "생년월일이 설정되지 않았습니다"
                
            birth_password = employee.birth.strftime('%Y%m%d')
            if birth_password != str(password):
                return None, "비밀번호가 일치하지 않습니다"
                
            # 로그인 성공 시 비밀번호 필드에 생년월일 저장 (자동 마이그레이션)
            employee.password = birth_password
            db.session.commit()
        
        # 4. 관리자 권한 확인
        admin = Admin.query.filter_by(admin_id=admin_id).first()
        if not admin:
            return None, "관리자 권한이 없습니다"
        
        return admin, None