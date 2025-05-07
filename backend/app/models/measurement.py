from app import db
from datetime import datetime

class DeviceMeasurement(db.Model):
    __tablename__ = 'DEVICE_MEASUREMENT'
    
    measurement_id = db.Column(db.String(10), primary_key=True)
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'))
    device_id = db.Column(db.String(10), db.ForeignKey('DEVICE.device_id'))
    measure_time = db.Column(db.DateTime, default=datetime.utcnow)
    battery = db.Column(db.Integer)
    hr = db.Column(db.Integer)  # 심박수
    sbp = db.Column(db.Integer)  # 수축기 혈압
    temp = db.Column(db.Float)  # 체온
    resp = db.Column(db.Integer)  # 호흡수
    spo2 = db.Column(db.Integer)  # 산소포화도
    acc_x = db.Column(db.Float)  # x축 가속도
    acc_y = db.Column(db.Float)  # y축 가속도
    acc_z = db.Column(db.Float)  # z축 가속도
    gyro_x = db.Column(db.Float)  # x축 자이로
    gyro_y = db.Column(db.Float)  # y축 자이로
    gyro_z = db.Column(db.Float)  # z축 자이로
    heat_risk = db.Column(db.Float)  # 온열질환 위험도
    fall_risk = db.Column(db.Float)  # 낙상 위험도
    
    def __repr__(self):
        return f'<DeviceMeasurement {self.measurement_id}: {self.emp_id} at {self.measure_time}>'


class HealthAnomaly(db.Model):
    __tablename__ = 'HEALTH_ANOMALY'
    
    anomaly_id = db.Column(db.String(10), primary_key=True)
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'))
    anomaly_time = db.Column(db.DateTime, default=datetime.utcnow)
    symptom = db.Column(db.String(255))
    risk = db.Column(db.String(50))
    loc_x = db.Column(db.Float)
    loc_y = db.Column(db.Float)
    
    def __repr__(self):
        return f'<HealthAnomaly {self.anomaly_id}: {self.emp_id} at {self.anomaly_time}>'