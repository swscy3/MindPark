import pandas as pd
import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'ScE1234**',
    'database': 'mindpark'
}

def insert_employee(cursor):
    df = pd.read_csv('/root/MindPark/database/datafile/employee.csv')
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO EMPLOYEE (
                emp_id, name, dept, position, phone, email, addr,
                birth, gender, age, picture, password
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['emp_id'], row['name'], row['dept'], row['position'], row['phone'],
            row['email'], row['addr'],
            row['birth'] if pd.notna(row['birth']) else None,
            row['gender'], row['age'], row['picture'], row['password']
        ))
    print("✅ EMPLOYEE 삽입 완료")
    
def insert_admin(cursor):
    df = pd.read_csv('/root/MindPark/database/datafile/admin.csv')
    df.columns = df.columns.str.strip()
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO ADMIN (
                admin_id
            ) VALUES (%s)
        """, (row['admin_id'],))
    print("✅ ADMIN 삽입 완료")

def insert_employee_health(cursor):
    df = pd.read_csv('/root/MindPark/database/datafile/employee_health.csv')
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO EMPLOYEE_HEALTH (
                emp_id, HT, HeartDisease, Pscyco, DM, CerevD, CKD, other_conditions
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row.emp_id, row.HT,
            row.HeartDisease, row.Pscyco,
            row.DM, row.CerevD, row.CKD,
            row.other_conditions if pd.notna(row.other_conditions) else None
        ))
    print("✅ EMPLOYEE_HEALTH 삽입 완료")

def insert_emergency_contact(cursor):
    df = pd.read_csv('/root/MindPark/database/datafile/emergency_contact.csv')
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO EMERGENCY_CONTACT (
                emp_id, contact_name, relation, contact_phone
            ) VALUES (%s, %s, %s, %s)
        """, (
            row.emp_id, row.contact_name, row.relation, row.contact_phone
        ))
    print("✅ EMERGENCY_CONTACT 삽입 완료")

def insert_device(cursor):
    df = pd.read_csv('/root/MindPark/database/datafile/device.csv')
    df.columns = df.columns.str.strip()  # 공백 제거 (혹시 모를 오염 대비)
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO DEVICE (
                device_id, product, manager_id, emp_id
            ) VALUES (%s, %s, %s, %s)
        """, (
            row['device_id'], row['product'], row['manager_id'], row['emp_id']
        ))
    print("✅ DEVICE 삽입 완료")

def insert_device_management(cursor):
    df = pd.read_csv('/root/MindPark/database/datafile/employee_attendance.csv')
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO EMPLOYEE_ATTENDANCE (
                device_id, emp_id, check_in, check_out
            ) VALUES (%s, %s, %s, %s)
        """, (
            row.device_id, row.emp_id,
            row.check_in if pd.notna(row.check_in) else None,
            row.check_out if pd.notna(row.check_out) else None
        ))
    print("✅ EMPLOYEE_ATTENDANCE 삽입 완료")
    
def insert_device_measurement(cursor):
    df = pd.read_csv('/root/MindPark/database/datafile/device_measurement.csv')
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO DEVICE_MEASUREMENT (
                measurement_id, emp_id, device_id, measure_time, battery,
                hr, temp, resp, spo2, walk,
                acc_x, acc_y, acc_z,
                gyro_x, gyro_y, gyro_z,
                loc_x, loc_y,
                heat_risk, fall_risk
            ) VALUES (%s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s,
                      %s, %s, %s,
                      %s, %s, %s,
                      %s, %s,
                      %s, %s)
        """, (
            row.measurement_id, row.emp_id, row.device_id,
            row.measure_time if pd.notna(row.measure_time) else None,
            row.battery,
            row.hr, row.temp, row.resp, row.spo2, row.walk,
            row.acc_x, row.acc_y, row.acc_z,
            row.gyro_x, row.gyro_y, row.gyro_z,
            row.loc_x if pd.notna(row.loc_x) else None,
            row.loc_y if pd.notna(row.loc_y) else None,
            row.heat_risk, row.fall_risk
        ))
    print("✅ DEVICE_MEASUREMENT 삽입 완료")


def insert_health_anomaly(cursor):
    df = pd.read_csv('/root/MindPark/database/datafile/health_anomaly.csv')
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO HEALTH_ANOMALY (
                anomaly_id, emp_id, anomaly_time, symptom, risk, status,
                action_content, loc_x, loc_y, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row.anomaly_id, row.emp_id,
            row.anomaly_time if pd.notna(row.anomaly_time) else None,
            row.symptom, row.risk, row.status,
            row.action_content if pd.notna(row.action_content) else None,
            row.loc_x if pd.notna(row.loc_x) else None,
            row.loc_y if pd.notna(row.loc_y) else None,
            row.updated_at if pd.notna(row.updated_at) else None
        ))
    print("✅ HEALTH_ANOMALY 삽입 완료")

def main():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 테이블 삽입 순서 중요 (외래키)
        insert_employee(cursor)
        insert_admin(cursor)
        insert_employee_health(cursor)
        insert_emergency_contact(cursor)
        insert_device(cursor)
        insert_device_management(cursor)
        insert_device_measurement(cursor)
        insert_health_anomaly(cursor)

        conn.commit()
        print("🎉 모든 데이터 삽입 완료")

    except mysql.connector.Error as err:
        print(f"❌ DB 오류: {err}")

    finally:
        if cursor: cursor.close()
        if conn: conn.close()

if __name__ == "__main__":
    main()
