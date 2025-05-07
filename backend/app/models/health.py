from app import db
from datetime import datetime

class EmployeeHealth(db.Model):
    __tablename__ = 'EMPLOYEE_HEALTH'
    
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'), primary_key=True)
    HT = db.Column(db.Boolean, default=False)
    HeartDisease = db.Column(db.Boolean, default=False)
    Pscyco = db.Column(db.Boolean, default=False)
    DM = db.Column(db.Boolean, default=False)
    CerevD = db.Column(db.Boolean, default=False)
    CKD = db.Column(db.Boolean, default=False)
    
    # 관계 설정
    employee = db.relationship('Employee', backref='health_info', uselist=False)
    
    def __repr__(self):
        return f'<EmployeeHealth {self.emp_id}>'


class EmergencyContact(db.Model):
    __tablename__ = 'EMERGENCY_CONTACT'
    
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'), primary_key=True)
    contact_name = db.Column(db.String(100))
    relation = db.Column(db.String(50))
    contact_phone = db.Column(db.String(20))
    
    # 관계 설정
    employee = db.relationship('Employee', backref='emergency_contact', uselist=False)
    
    def __repr__(self):
        return f'<EmergencyContact for {self.emp_id}: {self.contact_name}>'


class HealthAnomaly(db.Model):
    __tablename__ = 'HEALTH_ANOMALY'
    
    anomaly_id = db.Column(db.String(10), primary_key=True)
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'))
    anomaly_time = db.Column(db.DateTime, default=datetime.utcnow)
    symptom = db.Column(db.String(255))
    risk = db.Column(db.String(50))
    loc_x = db.Column(db.Float)
    loc_y = db.Column(db.Float)
    
    # 관계 설정
    employee = db.relationship('Employee', backref='health_anomalies')
    
    def __repr__(self):
        return f'<HealthAnomaly {self.anomaly_id}: {self.emp_id} at {self.anomaly_time}>'