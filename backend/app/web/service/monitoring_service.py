# app/web/services/monitoring_service.py
from app import db
from app.model import HealthAnomaly, Employee, Device, DeviceMeasurement, DeviceManagement
from app.util.time_utils import to_korea_time, utc_to_korea_date

class MonitoringService:
    @staticmethod
    def get_active_devices_count(korea_today):
        """한국시간 기준으로 활성 디바이스 수 계산"""
        try:
            device_managements = DeviceManagement.query.all()
            active_device_ids = set()
            
            for dm in device_managements:
                if dm.check_in:
                    check_in_korea_date = utc_to_korea_date(dm.check_in)
                    
                    if (check_in_korea_date == korea_today and dm.check_out is None):
                        active_device_ids.add(dm.device_id)
            
            return len(active_device_ids)
            
        except Exception as e:
            print(f"[ERROR] 활성 디바이스 수 계산 오류: {str(e)}")
            return 0

    @staticmethod
    def get_heat_risk_employees():
        """온열질환 위험자 조회"""
        try:
            heat_risks = db.session.query(HealthAnomaly, Employee)\
                .join(Employee, HealthAnomaly.emp_id == Employee.emp_id)\
                .filter(HealthAnomaly.symptom == '온열질환')\
                .filter(HealthAnomaly.status == '처리중')\
                .all()
            
            heat_risk_data = []
            for anomaly, employee in heat_risks:
                try:
                    latest_measurement = DeviceMeasurement.query\
                        .filter_by(emp_id=employee.emp_id)\
                        .order_by(DeviceMeasurement.measure_time.desc())\
                        .first()
                    
                    heat_risk_data.append({
                        "emp_id": employee.emp_id,
                        "name": employee.name,
                        "picture": employee.picture,
                        "vitals": {
                            "temperature": round(latest_measurement.temp, 1) if latest_measurement and latest_measurement.temp is not None else None,
                            "heart_rate": latest_measurement.hr if latest_measurement else None,
                            "respiration": latest_measurement.resp if latest_measurement else None
                        },
                        "risk_level": anomaly.risk,
                        "location": {
                            "latitude": anomaly.loc_x,
                            "longitude": anomaly.loc_y
                        },
                        "detected_time": to_korea_time(anomaly.anomaly_time),
                        "last_measurement_time": to_korea_time(latest_measurement.measure_time) if latest_measurement else None
                    })
                except Exception as emp_error:
                    print(f"[ERROR] 온열질환 직원 {employee.emp_id} 데이터 처리 오류: {str(emp_error)}")
                    continue
            
            return heat_risk_data
        except Exception as e:
            print(f"[ERROR] 온열질환 위험자 조회 오류: {str(e)}")
            return []

    @staticmethod
    def get_fall_risk_employees():
        """낙상 위험자 조회"""
        try:
            fall_risks = db.session.query(HealthAnomaly, Employee)\
                .join(Employee, HealthAnomaly.emp_id == Employee.emp_id)\
                .filter(HealthAnomaly.symptom == '낙상')\
                .filter(HealthAnomaly.status == '처리중')\
                .all()
            
            fall_risk_data = []
            for anomaly, employee in fall_risks:
                try:
                    latest_measurement = DeviceMeasurement.query\
                        .filter_by(emp_id=employee.emp_id)\
                        .order_by(DeviceMeasurement.measure_time.desc())\
                        .first()
                    
                    fall_risk_data.append({
                        "emp_id": employee.emp_id,
                        "name": employee.name,
                        "picture": employee.picture,
                        "vitals": {
                            "temperature": round(latest_measurement.temp, 1) if latest_measurement and latest_measurement.temp is not None else None,
                            "heart_rate": latest_measurement.hr if latest_measurement else None,
                            "respiration": latest_measurement.resp if latest_measurement else None
                        },
                        "risk_level": anomaly.risk,
                        "location": {
                            "latitude": anomaly.loc_x,
                            "longitude": anomaly.loc_y
                        },
                        "detected_time": to_korea_time(anomaly.anomaly_time),
                        "last_measurement_time": to_korea_time(latest_measurement.measure_time) if latest_measurement else None
                    })
                except Exception as emp_error:
                    print(f"[ERROR] 낙상 직원 {employee.emp_id} 데이터 처리 오류: {str(emp_error)}")
                    continue
            
            return fall_risk_data
        except Exception as e:
            print(f"[ERROR] 낙상 위험자 조회 오류: {str(e)}")
            return []

    @staticmethod
    def get_dashboard_data(korea_today):
        """대시보드 전체 데이터 조회"""
        heat_risk_data = MonitoringService.get_heat_risk_employees()
        fall_risk_data = MonitoringService.get_fall_risk_employees()
        
        total_devices = Device.query.count()
        active_devices = MonitoringService.get_active_devices_count(korea_today)
        inactive_devices = total_devices - active_devices
        
        return {
            "heat_risk_employees": heat_risk_data,
            "fall_risk_employees": fall_risk_data,
            "device_status": {
                "total_devices": total_devices,
                "active_devices": active_devices,
                "inactive_devices": inactive_devices,
                "calculation_date": korea_today.isoformat()
            }
        }