# app/web/services/employee_service.py
from app import db
from app.model import Employee, EmergencyContact, DeviceMeasurement, Device, DeviceManagement, Admin
from app.util.time_utils import to_korea_time, utc_to_korea_date

class EmployeeService:
    @staticmethod
    def get_attendance_status(emp_id, korea_today):
        """출근 상태 확인 (한국 시간 기준)"""
        try:
            attendances = DeviceManagement.query.filter_by(emp_id=emp_id).all()
            
            for attendance in attendances:
                if attendance.check_in:
                    check_in_korea_date = utc_to_korea_date(attendance.check_in)
                    
                    if (check_in_korea_date == korea_today and attendance.check_out is None):
                        return "출근중"
            
            return "미출근"
            
        except Exception as e:
            print(f"[ERROR] 출근 상태 확인 오류 (emp_id: {emp_id}): {str(e)}")
            return "미출근"

    @staticmethod
    def get_today_attendance_record(emp_id, korea_today):
        """오늘 출근 기록 조회 (한국 시간 기준)"""
        try:
            attendances = DeviceManagement.query.filter_by(emp_id=emp_id).all()
            
            for attendance in attendances:
                if attendance.check_in:
                    check_in_korea_date = utc_to_korea_date(attendance.check_in)
                    if check_in_korea_date == korea_today:
                        return attendance
            
            return None
            
        except Exception as e:
            print(f"[ERROR] 출근 기록 조회 오류 (emp_id: {emp_id}): {str(e)}")
            return None

    @staticmethod
    def get_employee_list(korea_today):
        """전체 직원 목록 조회 (Admin 제외)"""
        try:
            employees = Employee.query\
                .outerjoin(Admin, Employee.emp_id == Admin.admin_id)\
                .filter(Admin.admin_id.is_(None))\
                .all()
            
            employees_data = []
            
            for employee in employees:
                try:
                    attendance_status = EmployeeService.get_attendance_status(employee.emp_id, korea_today)
                    
                    employees_data.append({
                        "emp_id": employee.emp_id,
                        "name": employee.name,
                        "department": employee.dept,
                        "position": employee.position,
                        "attendance_status": attendance_status
                    })
                except Exception as emp_error:
                    print(f"[ERROR] 직원 {employee.emp_id} 처리 오류: {str(emp_error)}")
                    employees_data.append({
                        "emp_id": employee.emp_id,
                        "name": employee.name,
                        "department": employee.dept,
                        "position": employee.position,
                        "attendance_status": "확인불가"
                    })
            
            return employees_data
            
        except Exception as e:
            print(f"[ERROR] 직원 목록 조회 오류: {str(e)}")
            raise e

    @staticmethod
    def get_employee_detail(emp_id, korea_today):
        """직원 상세정보 조회"""
        try:
            # 직원 기본 정보
            employee = Employee.query.filter_by(emp_id=emp_id).first()
            if not employee:
                return None
            
            # 응급 연락처
            emergency_contact = EmergencyContact.query.filter_by(emp_id=emp_id).first()
            emergency_contact_info = None
            if emergency_contact:
                emergency_contact_info = f"{emergency_contact.contact_name} ({emergency_contact.relation}) - {emergency_contact.contact_phone}"
            
            # 최신 생체 데이터
            latest_measurement = DeviceMeasurement.query\
                .filter_by(emp_id=emp_id)\
                .order_by(DeviceMeasurement.measure_time.desc())\
                .first()
            
            # 디바이스 정보
            device = None
            if latest_measurement:
                device = Device.query.filter_by(device_id=latest_measurement.device_id).first()
            
            # 출근 상태
            attendance_status = EmployeeService.get_attendance_status(emp_id, korea_today)
            
            return {
                "basic_info": {
                    "emp_id": employee.emp_id,
                    "name": employee.name,
                    "age": employee.age,
                    "gender": employee.gender,
                    "department": employee.dept,
                    "position": employee.position
                },
                "contact_info": {
                    "emergency_contact": emergency_contact_info
                },
                "health_data": {
                    "heart_rate": latest_measurement.hr if latest_measurement else None,
                    "spo2": latest_measurement.spo2 if latest_measurement else None,
                    "temperature": latest_measurement.temp if latest_measurement else None,
                    "steps": latest_measurement.walk if latest_measurement else None,
                    "last_measurement_time": to_korea_time(latest_measurement.measure_time) if latest_measurement else None
                },
                "device_info": {
                    "device_name": device.product if device else None,
                    "battery_level": latest_measurement.battery if latest_measurement else None
                },
                "location_info": {
                    "latitude": latest_measurement.loc_y if latest_measurement else None,
                    "longitude": latest_measurement.loc_x if latest_measurement else None
                },
                "attendance_info": {
                    "status": attendance_status,
                    "check_date": korea_today.isoformat()
                }
            }
            
        except Exception as e:
            print(f"[ERROR] 직원 상세정보 조회 오류 (emp_id: {emp_id}): {str(e)}")
            raise e