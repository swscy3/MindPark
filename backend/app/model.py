from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Employee(db.Model):
    __tablename__ = 'EMPLOYEE'
    
    emp_id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100))
    dept = db.Column(db.String(100))
    position = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    addr = db.Column(db.String(255))
    birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    picture = db.Column(db.String(255))
    password = db.Column(db.String(255))
    
    # 관계는 각 관련 모델에서 정의됨
    
    def set_password(self, password):
        """비밀번호를 저장"""
        self.password = password
        
    def check_password(self, password):
        """입력된 비밀번호가 저장된 비밀번호와 일치하는지 확인"""
        # 비밀번호가 설정되지 않은 경우 생년월일로 확인 (이전 방식과의 호환성)
        if not self.password and self.birth:
            birth_password = self.birth.strftime('%Y%m%d')
            if password == birth_password:
                # 로그인 성공시 생년월일을 비밀번호로 저장 (자동 업그레이드)
                self.password = birth_password
                return True
            return False
        
        # 저장된 비밀번호와 직접 비교
        return self.password == password
    
    def set_default_password(self):
        """생년월일을 초기 비밀번호로 설정"""
        if self.birth:
            self.password = self.birth.strftime('%Y%m%d')
            return True
        return False
    
    def __repr__(self):
        return f'<Employee {self.emp_id}: {self.name}>'


class Admin(db.Model):
    __tablename__ = 'ADMIN'
    
    admin_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'), primary_key=True)
    
    # 관계 설정
    managed_devices = db.relationship('Device', backref='admin', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Admin {self.admin_id}>'


class Device(db.Model):
    __tablename__ = 'DEVICE'
    
    device_id = db.Column(db.String(10), primary_key=True)
    product = db.Column(db.String(100))
    manager_id = db.Column(db.String(10), db.ForeignKey('ADMIN.admin_id'))
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'))  # 직원 ID 외래 키 추가
    
    # 관계 설정
    managements = db.relationship('DeviceManagement', backref='device', cascade='all, delete-orphan')
    measurements = db.relationship('DeviceMeasurement', backref='device', cascade='all, delete-orphan')
    employee = db.relationship('Employee', backref='devices')  # Employee와의 관계 추가
    
    def __repr__(self):
        return f'<Device {self.device_id}: {self.product}>'


class DeviceManagement(db.Model):
    __tablename__ = 'EMPLOYEE_ATTENDANCE'
    
    device_id = db.Column(db.String(10), db.ForeignKey('DEVICE.device_id'), primary_key=True)
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'), primary_key=True)
    check_in = db.Column(db.DateTime, primary_key=True)
    check_out = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<DeviceManagement {self.device_id} - {self.emp_id}: {self.check_in}>'


class DeviceMeasurement(db.Model):
    __tablename__ = 'DEVICE_MEASUREMENT'
    
    measurement_id = db.Column(db.String(25), primary_key=True)
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'))
    device_id = db.Column(db.String(10), db.ForeignKey('DEVICE.device_id'))
    measure_time = db.Column(db.DateTime, default=datetime.utcnow)
    battery = db.Column(db.Integer)
    hr = db.Column(db.Integer)  # 심박수
    temp = db.Column(db.Float)  # 체온
    resp = db.Column(db.Integer)  # 호흡수
    spo2 = db.Column(db.Integer)  # 산소포화도
    walk = db.Column(db.Integer)  # 작업 관련 정보
    loc_x = db.Column(db.Float)  # 경도
    loc_y = db.Column(db.Float)  # 위도
    acc_x = db.Column(db.Float)  # x축 가속도
    acc_y = db.Column(db.Float)  # y축 가속도
    acc_z = db.Column(db.Float)  # z축 가속도
    gyro_x = db.Column(db.Float)  # x축 자이로
    gyro_y = db.Column(db.Float)  # y축 자이로
    gyro_z = db.Column(db.Float)  # z축 자이로
    heat_risk = db.Column(db.String(5))  # 온열질환 위험도
    fall_risk = db.Column(db.String(5))  # 낙상 위험도

    def __repr__(self):
        return f'<DeviceMeasurement {self.measurement_id}: {self.emp_id} at {self.measure_time}>'


class EmployeeHealth(db.Model):
    __tablename__ = 'EMPLOYEE_HEALTH'
    
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'), primary_key=True)
    HT = db.Column(db.Boolean, default=False)
    HeartDisease = db.Column(db.Boolean, default=False)
    Pscyco = db.Column(db.Boolean, default=False)
    DM = db.Column(db.Boolean, default=False)
    CerevD = db.Column(db.Boolean, default=False)
    CKD = db.Column(db.Boolean, default=False)
    other_conditions = db.Column(db.String(255), nullable=False, default="")
    
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
    # 새로 추가된 필드들
    status = db.Column(db.String(20), default='처리 중')  # '처리 중', '완료'
    action_content = db.Column(db.Text)  # 조치 내용

    # 발생시간
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    employee = db.relationship('Employee', backref='health_anomalies')
    
    def to_dict(self):
        return {
            'anomaly_id': self.anomaly_id,
            'emp_id': self.emp_id,
            'emp_name': self.employee.name if self.employee else '',
            'anomaly_time': self.anomaly_time.isoformat() if self.anomaly_time else None,
            'symptom': self.symptom,
            'risk': self.risk,
            'status': self.status,
            'action_content': self.action_content,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<HealthAnomaly {self.anomaly_id}: {self.emp_id} at {self.anomaly_time}>'


class TokenBlocklist(db.Model):
    """
    JWT 토큰 블랙리스트를 저장하는 모델
    
    이 모델은 로그아웃된 JWT 토큰을 추적하여 해당 토큰이
    더 이상 API에 접근하지 못하도록 합니다.
    """
    __tablename__ = 'TOKEN_BLOCKLIST'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    jti = db.Column(db.String(36), nullable=False, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<TokenBlocklist {self.jti}>'