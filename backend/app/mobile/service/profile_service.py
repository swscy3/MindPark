from app.model import Employee, EmployeeHealth, EmergencyContact, db


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
            health_fields = ['HT', 'HeartDisease', 'Pscyco', 'DM', 'CerevD', 'CKD', 'other_conditions']
            if any(field in data for field in health_fields):
                health_info = EmployeeHealth.query.filter_by(emp_id=emp_id).first()
                
                # 건강 정보가 없으면 새로 생성
                if not health_info:
                    health_info = EmployeeHealth(emp_id=emp_id)
                    health_info.other_conditions = ""  # 기본값 설정
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
    
    @staticmethod
    def get_profile(emp_id):
        """
        직원 프로필 정보 조회 (카멜케이스 응답)
        
        Args:
            emp_id (str): 직원 ID
            
        Returns:
            dict: 프로필 정보 또는 None
        """
        try:
            # 직원 기본 정보 조회
            employee = Employee.query.filter_by(emp_id=emp_id).first()
            if not employee:
                return None
            
            # 건강 정보 조회
            health_info = EmployeeHealth.query.filter_by(emp_id=emp_id).first()
            
            # 보호자 정보 조회
            emergency_contact = EmergencyContact.query.filter_by(emp_id=emp_id).first()
            
            # 질병 정보를 한국어 배열로 변환
            diseases = []
            disease_mapping = {
                'HT': '고혈압',
                'HeartDisease': '심장질환', 
                'Pscyco': '정신질환',
                'DM': '당뇨병',
                'CerevD': '뇌혈관질환',
                'CKD': '만성신장질환'
            }
            
            if health_info:
                for field, korean_name in disease_mapping.items():
                    if getattr(health_info, field, False):
                        diseases.append(korean_name)
            
            # 프로필 데이터 구성 (카멜케이스)
            profile_data = {
                # 직원 기본 정보 (카멜케이스)
                "empId": employee.emp_id,
                "name": employee.name,
                "age": str(employee.age) if employee.age else None,  # 문자열로 변환 (로그인 응답과 일치)
                
                # 질병 정보 (한국어 배열)
                "diseases": diseases,
                "otherConditions": health_info.other_conditions if health_info and health_info.other_conditions else None,
                
                # 보호자 정보 (카멜케이스)
                "guardianName": emergency_contact.contact_name if emergency_contact else None,
                "guardianRelation": emergency_contact.relation if emergency_contact else None,
                "guardianPhone": emergency_contact.contact_phone if emergency_contact else None
            }
            
            return profile_data
            
        except Exception as e:
            return None

    @staticmethod
    def get_profile_detailed(emp_id):
        """
        상세 프로필 정보 조회 (모든 필드 포함)
        
        Args:
            emp_id (str): 직원 ID
            
        Returns:
            dict: 상세 프로필 정보 또는 None
        """
        try:
            # 직원 기본 정보 조회
            employee = Employee.query.filter_by(emp_id=emp_id).first()
            if not employee:
                return None
            
            # 건강 정보 조회
            health_info = EmployeeHealth.query.filter_by(emp_id=emp_id).first()
            
            # 보호자 정보 조회
            emergency_contact = EmergencyContact.query.filter_by(emp_id=emp_id).first()
            
            # 상세 프로필 데이터 구성 (개발/관리용)
            profile_data = {
                # 직원 기본 정보
                "empId": employee.emp_id,
                "name": employee.name,
                "dept": employee.dept,
                "position": employee.position,
                "phone": employee.phone,
                "email": employee.email,
                "addr": employee.addr,
                "birth": employee.birth.isoformat() if employee.birth else None,
                "gender": employee.gender,
                "age": employee.age,
                
                # 건강 정보 (boolean 값들)
                "HT": health_info.HT if health_info else False,
                "HeartDisease": health_info.HeartDisease if health_info else False,
                "Pscyco": health_info.Pscyco if health_info else False,
                "DM": health_info.DM if health_info else False,
                "CerevD": health_info.CerevD if health_info else False,
                "CKD": health_info.CKD if health_info else False,
                "otherConditions": health_info.other_conditions if health_info else "",
                
                # 보호자 정보
                "guardianName": emergency_contact.contact_name if emergency_contact else "",
                "guardianRelation": emergency_contact.relation if emergency_contact else "",
                "guardianPhone": emergency_contact.contact_phone if emergency_contact else ""
            }
            
            return profile_data
            
        except Exception as e:
            return None