from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token
from datetime import datetime

app = Flask(__name__)

# ✅ DB 및 JWT 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:ScE1234**@localhost:3306/mindpark'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'
db = SQLAlchemy(app)
jwt = JWTManager(app)

# ✅ DB 모델 정의
class EmergencyContact(db.Model):
    __tablename__ = 'EMERGENCY_CONTACT'
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'), primary_key=True)
    contact_name = db.Column(db.String(100))
    relation = db.Column(db.String(50))
    contact_phone = db.Column(db.String(20))

class EmployeeDisease(db.Model):
    __tablename__ = 'EMPLOYEE_DISEASE'
    emp_id = db.Column(db.String(10), db.ForeignKey('EMPLOYEE.emp_id'), primary_key=True)
    HT = db.Column(db.Integer)
    HeartDisease = db.Column(db.Integer)
    Pscyco = db.Column(db.Integer)
    DM = db.Column(db.Integer)
    CerevD = db.Column(db.Integer)
    CKD = db.Column(db.Integer)

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

    def check_password(self, input_password):
        if not self.birth:
            return False
        try:
            birth_str = self.birth.strftime('%Y%m%d')
            return birth_str == input_password
        except Exception as e:
            print(f"[비밀번호 검사 오류] {e}")
            return False

@app.route('/')
def log():
    return "Hello world"

@app.route('/api/mobile/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    user_id = data.get('id')
    password = data.get('password')

    if not user_id or not password:
        return jsonify({"error": "아이디와 비밀번호는 필수입니다."}), 400

    user = Employee.query.filter_by(emp_id=user_id).first()

    if not user or not user.check_password(password):
        app.logger.warning(f"로그인 실패: {user_id}")
        return jsonify({"error": "아이디 또는 비밀번호가 올바르지 않습니다."}), 401

    token = create_access_token(identity=user.emp_id)

    contact = EmergencyContact.query.filter_by(emp_id=user.emp_id).first()
    disease = EmployeeDisease.query.filter_by(emp_id=user.emp_id).first()

    return jsonify({
        "message": "로그인 성공",
        "token": token,
        "user": {
            "emp_id": user.emp_id,
            "name": user.name,
            "contact": {
                "name": contact.contact_name if contact else "",
                "relation": contact.relation if contact else "",
                "phone": contact.contact_phone if contact else ""
            },
            "diseases": {
                "HT": bool(disease.HT) if disease else False,
                "HeartDisease": bool(disease.HeartDisease) if disease else False,
                "Pscyco": bool(disease.Pscyco) if disease else False,
                "DM": bool(disease.DM) if disease else False,
                "CerevD": bool(disease.CerevD) if disease else False,
                "CKD": bool(disease.CKD) if disease else False
            }
        }
    }), 200

if __name__ == '__main__':
    app.run(port=3000, debug=True, host='0.0.0.0')
