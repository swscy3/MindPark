import mysql.connector

# DB 접속 정보
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ScE1234**',
    'database': 'mindpark'
}


# 다중 테이블 생성 SQL (외래 키 포함, CASCADE 지원 안됨 → 제거)
schema_sql = """
DROP TABLE IF EXISTS EMPLOYEE;
DROP TABLE IF EXISTS ADMIN;
DROP TABLE IF EXISTS EMPLOYEE_HEALTH;
DROP TABLE IF EXISTS EMPLOYEE_ATTENDANCE;
DROP TABLE IF EXISTS DEVICE;
DROP TABLE IF EXISTS EMERGENCY_CONTACT;
DROP TABLE IF EXISTS DEVICE_MEASUREMENT;
DROP TABLE IF EXISTS HEALTH_ANOMALY;
DROP TABLE IF EXISTS TOKEN_BLOCKLIST;

CREATE TABLE EMPLOYEE (
    emp_id CHAR(10) PRIMARY KEY,
    name VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
    dept VARCHAR(100),
    position VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    addr VARCHAR(255),
    birth DATE,
    gender VARCHAR(10),
    age INT,
    picture VARCHAR(255),
    password VARCHAR(12),
    CHECK (CHAR_LENGTH(password) BETWEEN 4 AND 12)
);

CREATE TABLE ADMIN (
    admin_id CHAR(10) PRIMARY KEY,
    FOREIGN KEY (admin_id) REFERENCES EMPLOYEE(emp_id)
);

CREATE TABLE EMPLOYEE_HEALTH (
    emp_id CHAR(10) PRIMARY KEY,
    HT BOOLEAN,
    HeartDisease BOOLEAN,
    Pscyco BOOLEAN,
    DM BOOLEAN,
    CerevD BOOLEAN,
    CKD BOOLEAN,
    other_conditions VARCHAR(255),
    FOREIGN KEY (emp_id) REFERENCES EMPLOYEE(emp_id)
);

CREATE TABLE EMERGENCY_CONTACT (
    emp_id CHAR(10) PRIMARY KEY,
    contact_name VARCHAR(100),
    relation VARCHAR(50),
    contact_phone VARCHAR(20),
    FOREIGN KEY (emp_id) REFERENCES EMPLOYEE(emp_id)
);

CREATE TABLE DEVICE (
    device_id CHAR(10) PRIMARY KEY,
    product VARCHAR(100),
    manager_id CHAR(10),
    emp_id CHAR(10),
    FOREIGN KEY (manager_id) REFERENCES EMPLOYEE(emp_id),
    FOREIGN KEY (emp_id) REFERENCES EMPLOYEE(emp_id)
);

CREATE TABLE EMPLOYEE_ATTENDANCE (
    device_id CHAR(10),
    emp_id CHAR(10),
    check_in DATETIME,
    check_out DATETIME,
    PRIMARY KEY (device_id, emp_id, check_in),
    FOREIGN KEY (device_id) REFERENCES DEVICE(device_id),
    FOREIGN KEY (emp_id) REFERENCES EMPLOYEE(emp_id)
);

CREATE TABLE DEVICE_MEASUREMENT (
    measurement_id CHAR(25) PRIMARY KEY,
    emp_id CHAR(10),
    device_id CHAR(10),
    measure_time DATETIME,
    battery INT,
    hr INT,
    temp FLOAT,
    resp INT,
    spo2 INT,
    walk INT,
    acc_x FLOAT,
    acc_y FLOAT,
    acc_z FLOAT,
    gyro_x FLOAT,
    gyro_y FLOAT,
    gyro_z FLOAT,
    loc_x FLOAT, 
    loc_y FLOAT,
    heat_risk VARCHAR(5),
    fall_risk VARCHAR(5),
    FOREIGN KEY (emp_id) REFERENCES EMPLOYEE(emp_id),
    FOREIGN KEY (device_id) REFERENCES DEVICE(device_id)
);

CREATE TABLE HEALTH_ANOMALY (
    anomaly_id CHAR(10) PRIMARY KEY,
    emp_id CHAR(10),
    anomaly_time DATETIME,
    symptom VARCHAR(255),
    risk VARCHAR(50),
    status VARCHAR(255),
    action_content VARCHAR(255),
    loc_x FLOAT,
    loc_y FLOAT,
    updated_at DATETIME,
    FOREIGN KEY (emp_id) REFERENCES EMPLOYEE(emp_id)
);

CREATE TABLE TOKEN_BLOCKLIST (
    id INT AUTO_INCREMENT PRIMARY KEY,
    jti VARCHAR(36) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    INDEX idx_jti (jti)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

"""

def create_schema():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 외래 키 무시하고 테이블 삭제 가능하도록 설정
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")

        for statement in schema_sql.strip().split(';'):
            if statement.strip():
                cursor.execute(statement)

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print("✅ 모든 테이블이 성공적으로 생성되었습니다.")
        
    except mysql.connector.Error as err:
        print(f"❌ 오류 발생: {err}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    create_schema()
