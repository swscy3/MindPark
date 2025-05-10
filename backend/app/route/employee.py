from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.employee import Employee
from app.models.health import EmployeeHealth, EmergencyContact
from app.schemas.employee import EmployeeSchema, EmployeeHealthSchema, EmergencyContactSchema

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/mypage', methods=['GET'])
@jwt_required()
def get_mypage():
    # URL 파라미터에서 사번 조회, 없으면 현재 로그인한 사용자의 사번 사용
    current_user_id = get_jwt_identity()
    emp_id = request.args.get('emp_id', current_user_id)
    
    # 직원 정보 조회
    employee = Employee.query.get(emp_id)
    if not employee:
        return jsonify({"error": "직원 정보를 찾을 수 없습니다"}), 404
    
    # 건강 정보 조회
    health_info = EmployeeHealth.query.get(emp_id)
    
    # 보호자 정보 조회
    emergency_contact = EmergencyContact.query.get(emp_id)
    
    # 응답 데이터 구성
    employee_schema = EmployeeSchema()
    health_schema = EmployeeHealthSchema()
    contact_schema = EmergencyContactSchema()
    
    response_data = {
        "emp_id": employee.emp_id,
        "emp_name": employee.name,
        "emp_phoneNumber": employee.phone,
        "department": employee.dept,
        "has_disease": any([
            health_info.HT if health_info else False,
            health_info.HeartDisease if health_info else False,
            health_info.Pscyco if health_info else False,
            health_info.DM if health_info else False,
            health_info.CerevD if health_info else False,
            health_info.CKD if health_info else False
        ]),
        "guardian_name": emergency_contact.contact_name if emergency_contact else None,
        "guardian_rel": emergency_contact.relation if emergency_contact else None,
        "guardian_phone": emergency_contact.contact_phone if emergency_contact else None,
        "etc_disease": "당뇨" if health_info and health_info.DM else ""
    }
    
    return jsonify(response_data), 200

@employee_bp.route('/mypage', methods=['PUT'])
@jwt_required()
def update_mypage():
    # 현재 로그인한 사용자의 ID 가져오기
    current_user_id = get_jwt_identity()
    
    # 요청 데이터 가져오기
    data = request.json
    
    # 직원 정보 업데이트
    employee = Employee.query.get(current_user_id)
    if not employee:
        return jsonify({"error": "직원 정보를 찾을 수 없습니다"}), 404
    
    # 건강 정보 업데이트
    health_info = EmployeeHealth.query.get(current_user_id)
    if not health_info:
        health_info = EmployeeHealth(emp_id=current_user_id)
        db.session.add(health_info)
    
    # 보호자 정보 업데이트
    emergency_contact = EmergencyContact.query.get(current_user_id)
    if not emergency_contact:
        emergency_contact = EmergencyContact(emp_id=current_user_id)
        db.session.add(emergency_contact)
    
    # 데이터 업데이트
    if 'guardian_name' in data:
        emergency_contact.contact_name = data['guardian_name']
    if 'guardian_rel' in data:
        emergency_contact.relation = data['guardian_rel']
    if 'guardian_phone' in data:
        emergency_contact.contact_phone = data['guardian_phone']
    
    # 질병 정보 업데이트 (has_disease가 있는 경우)
    if 'has_disease' in data:
        has_disease = data['has_disease']
        if 'etc_disease' in data and data['etc_disease'] == '당뇨':
            health_info.DM = has_disease
    
    db.session.commit()
    
    return jsonify({"message": "정보가 업데이트되었습니다"}), 200