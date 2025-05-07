from app import db
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
    password_hash = db.Column(db.String(128))
    
    # 관계는 각 관련 모델에서 정의됨
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Employee {self.emp_id}: {self.name}>'


class Admin(db.Model):
    __tablename__ = 'ADMIN'
    
    admin_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'), primary_key=True)
    
    # 관계 설정
    managed_devices = db.relationship('Device', backref='admin', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Admin {self.admin_id}>'