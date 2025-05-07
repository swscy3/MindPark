from app import db
from datetime import datetime

class Device(db.Model):
    __tablename__ = 'DEVICE'
    
    device_id = db.Column(db.String(10), primary_key=True)
    product = db.Column(db.String(100))
    manager_id = db.Column(db.String(10), db.ForeignKey('ADMIN.admin_id'))
    
    # 관계 설정
    managements = db.relationship('DeviceManagement', backref='device', cascade='all, delete-orphan')
    failures = db.relationship('DeviceFailure', backref='device', cascade='all, delete-orphan')
    measurements = db.relationship('DeviceMeasurement', backref='device', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Device {self.device_id}: {self.product}>'


class DeviceManagement(db.Model):
    __tablename__ = 'DEVICE_MANAGEMENT'
    
    device_id = db.Column(db.String(10), db.ForeignKey('DEVICE.device_id'), primary_key=True)
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'), primary_key=True)
    check_in = db.Column(db.DateTime, primary_key=True)
    check_out = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<DeviceManagement {self.device_id} - {self.emp_id}: {self.check_in}>'


class DeviceFailure(db.Model):
    __tablename__ = 'DEVICE_FAILURE'
    
    fail_id = db.Column(db.String(10), primary_key=True)
    device_id = db.Column(db.String(10), db.ForeignKey('DEVICE.device_id'))
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'))
    fail_time = db.Column(db.DateTime, default=datetime.utcnow)
    reason = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<DeviceFailure {self.fail_id}: {self.device_id}>'