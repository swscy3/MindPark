from ...model import Employee, EmployeeHealth, EmergencyContact, db

class ProfileService:
    @staticmethod
    def update_profile(emp_id, data):
        """
        마이페이지 정보 수정
        
        Args:
            emp_id (str): 직원 ID
            data (dict): 업데이트할 정보
            
        Returns:
            tuple: (성공 여부, 메시지)
        """
        try:
            # 직원 기본 정보 조회
            employee = Employee.query.filter_by(emp_id=emp_id).first()
            if not employee:
                return False, "직원 정보를 찾을 수 없습니다"
            
            # 직원 전화번호 업데이트
            if 'phone' in data:
                employee.phone = data['phone']
            
            # 건강 정보 업데이트
            health_fields = ['HT', 'HeartDisease', 'Pscyco', 'DM', 'CerevD', 'CKD']
            if any(field in data for field in health_fields):
                health_info = EmployeeHealth.query.filter_by(emp_id=emp_id).first()
                
                # 건강 정보가 없으면 새로 생성
                if not health_info:
                    health_info = EmployeeHealth(emp_id=emp_id)
                    db.session.add(health_info)
                
                # 건강 정보 필드 업데이트
                for field in health_fields:
                    if field in data:
                        setattr(health_info, field, data[field])
            
            # 보호자 정보 업데이트
            guardian_fields = ['guardian_name', 'guardian_rel', 'guardian_phone']
            if any(field in data for field in guardian_fields):
                emergency_contact = EmergencyContact.query.filter_by(emp_id=emp_id).first()
                
                # 보호자 정보가 없으면 새로 생성
                if not emergency_contact:
                    emergency_contact = EmergencyContact(emp_id=emp_id)
                    db.session.add(emergency_contact)
                
                # 보호자 정보 업데이트
                if 'guardian_name' in data:
                    emergency_contact.contact_name = data['guardian_name']
                if 'guardian_rel' in data:
                    emergency_contact.relation = data['guardian_rel']
                if 'guardian_phone' in data:
                    emergency_contact.contact_phone = data['guardian_phone']
            
            # 변경사항 저장
            db.session.commit()
            
            return True, "정보가 성공적으로 업데이트되었습니다"
            
        except Exception as e:
            db.session.rollback()
            return False, f"서버 오류가 발생했습니다: {str(e)}"