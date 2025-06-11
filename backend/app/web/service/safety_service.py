# app/web/services/safety_service.py
import os
from app import db
from app.model import HealthAnomaly, Employee, EmergencyContact, DeviceMeasurement, Device
from app.util.time_utils import to_korea_time

class SafetyService:
    @staticmethod
    def convert_picture_to_url(picture_path):
        """절대 경로를 웹 URL로 변환"""
        if not picture_path:
            return None
        
        filename = os.path.basename(picture_path)
        if not os.path.splitext(filename)[1]:
            filename += '.jpg'
        
        return f"/uploads/pictures/{filename}"

    @staticmethod
    def format_employee_data(anomaly, employee, emergency_contact, latest_measurement, device):
        """직원 데이터를 JSON 형태로 포맷팅"""
        return {
            "emp_id": employee.emp_id,
            "basic_info": {
                "name": employee.name,
                "age": employee.age,
                "gender": employee.gender,
                "department": employee.dept,
                "position": employee.position,
                "picture": SafetyService.convert_picture_to_url(employee.picture)
            },
            "emergency_contact": {
                "contact_name": emergency_contact.contact_name if emergency_contact else None,
                "relation": emergency_contact.relation if emergency_contact else None,
                "phone": emergency_contact.contact_phone if emergency_contact else None
            },
            "current_vitals": {
                "heart_rate": latest_measurement.hr if latest_measurement else None,
                "spo2": latest_measurement.spo2 if latest_measurement else None,
                "temperature": latest_measurement.temp if latest_measurement else None,
                "respiration": latest_measurement.resp if latest_measurement else None,
                "steps": latest_measurement.walk if latest_measurement else None,
                "measurement_time": to_korea_time(latest_measurement.measure_time) if latest_measurement and latest_measurement.measure_time else None
            },
            "device_info": {
                "device_name": device.product if device else None,
                "battery_level": latest_measurement.battery if latest_measurement else None,
                "device_id": device.device_id if device else None
            },
            "location": {
                "latitude": anomaly.loc_x,
                "longitude": anomaly.loc_y,
                "location_time": to_korea_time(anomaly.anomaly_time)
            },
            "risk_info": {
                "anomaly_id": anomaly.anomaly_id,
                "risk_level": anomaly.risk,
                "symptom": anomaly.symptom,
                "detected_time": to_korea_time(anomaly.anomaly_time),
                "status": anomaly.status,
                "action_content": anomaly.action_content
            }
        }

    @staticmethod
    def get_employees_by_risk_level(risk_level):
        """위험도별 직원 데이터 조회"""
        try:
            anomalies = HealthAnomaly.query\
                .filter(HealthAnomaly.risk == risk_level)\
                .filter(HealthAnomaly.status == '처리중')\
                .order_by(HealthAnomaly.anomaly_time.desc())\
                .all()
            
            employees_data = []
            
            for anomaly in anomalies:
                try:
                    employee = Employee.query.filter_by(emp_id=anomaly.emp_id).first()
                    if not employee:
                        continue
                        
                    emergency_contact = EmergencyContact.query.filter_by(emp_id=anomaly.emp_id).first()
                    
                    latest_measurement = DeviceMeasurement.query\
                        .filter_by(emp_id=anomaly.emp_id)\
                        .order_by(DeviceMeasurement.measure_time.desc())\
                        .first()
                    
                    device = None
                    if latest_measurement:
                        device = Device.query.filter_by(device_id=latest_measurement.device_id).first()
                    
                    employee_data = SafetyService.format_employee_data(
                        anomaly, employee, emergency_contact, latest_measurement, device
                    )
                    employees_data.append(employee_data)
                    
                except Exception as emp_error:
                    print(f"[ERROR] 직원 {anomaly.emp_id} 데이터 처리 오류: {str(emp_error)}")
                    continue
            
            return employees_data
            
        except Exception as e:
            print(f"[ERROR] 위험도 {risk_level} 직원 데이터 조회 오류: {str(e)}")
            raise e