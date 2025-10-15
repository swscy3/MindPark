from datetime import datetime, time
from zoneinfo import ZoneInfo
import uuid
import pandas as pd
import numpy as np
import random
import os
from sqlalchemy import func
import tensorflow as tf

from ...model import DeviceMeasurement, DeviceManagement, EmployeeHealth, Employee, HealthAnomaly, Admin  # ✅ Admin 추가
from ... import db

# acc_gyr 데이터 로딩 (전역에서 한 번만)
ACC_GYR_CSV_PATH = os.environ.get('ACC_GYR_CSV_PATH', '/root/proj/MindPark/backend/app/mobile/service/acc_gyr.csv')
acc_gyr_df = pd.read_csv(ACC_GYR_CSV_PATH)

class DeviceService:
    @staticmethod
    def process_measurement(current_user, device, data):
        try:
            if current_user == "TEST_USER":
                current_user = "EN0003"

            kst_now = datetime.now(ZoneInfo("Asia/Seoul"))
            measure_time = kst_now

            base_row = {
                "emp_id": current_user,
                "device_id": device.device_id,
                "battery": data.get("battery"),
                "hr": data.get("hr"),
                "temp": round(data.get("temp"), 1) if data.get("temp") is not None else None,
                "resp": data.get("resp"),
                "spo2": data.get("spo2"),
                "walk": random.randint(4000, 6000),
                "acc_x": data.get("acc_x"),
                "acc_y": data.get("acc_y"),
                "acc_z": data.get("acc_z"),
                "gyro_x": data.get("gyro_x"),
                "gyro_y": data.get("gyro_y"),
                "gyro_z": data.get("gyro_z"),
                "loc_x": data.get("loc_x"),
                "loc_y": data.get("loc_y"),
                "measure_time": measure_time
            }

            def attach_health_info_and_profile(emp_id, row):
                health = EmployeeHealth.query.filter_by(emp_id=emp_id).first()
                profile = Employee.query.filter_by(emp_id=emp_id).first()

                row['HT'] = health.HT if health else False
                row['HeartDisease'] = health.HeartDisease if health else False
                row['Pscyco'] = health.Pscyco if health else False
                row['DM'] = health.DM if health else False
                row['CerevD'] = health.CerevD if health else False
                row['CKD'] = health.CKD if health else False

                if profile and profile.gender == 'M':
                    row['gender'] = 0
                elif profile and profile.gender == 'F':
                    row['gender'] = 1
                else:
                    row['gender'] = -1

                row['age'] = profile.age if profile else -1
                row['location'] = 1
                return row

            base_row = attach_health_info_and_profile(current_user, base_row)

            today = kst_now.date()
            start_time = datetime.combine(today, time(6, 30), tzinfo=ZoneInfo("Asia/Seoul"))
            emp_ids = db.session.query(DeviceManagement.emp_id).filter(
                DeviceManagement.check_in >= start_time
            ).distinct().all()
            emp_ids = [emp[0] for emp in emp_ids if emp[0] != current_user]

            # 🔽 관리자 제외 처리
            admin_ids = db.session.query(Admin.admin_id).all()
            admin_ids = [admin[0] for admin in admin_ids]
            emp_ids = [emp_id for emp_id in emp_ids if emp_id not in admin_ids]

            if len(emp_ids) < 3:
                return {"status": "error", "message": "온열질환 및 낙상 더미 생성을 위한 출근 인원이 3명 이상 필요합니다."}

            def random_location():
                base_lat, base_lon = 34.910319, 126.4361795
                delta_lat = random.uniform(-0.0045, 0.0045)
                delta_lon = random.uniform(-0.0045, 0.0045)
                return base_lat + delta_lat, base_lon + delta_lon

            dummy_rows = []
            labels_normal = ['sit', 'step', 'walk']

            random.shuffle(emp_ids)
            fall_emp_ids = random.sample(emp_ids, 2)
            for i, fall_label in enumerate(['fall', 'light']):
                row = base_row.copy()
                row['emp_id'] = fall_emp_ids[i]
                row['battery'] = random.randint(0, 100)
                row['hr'] = random.uniform(60, 99)
                row['temp'] = round(random.uniform(35.6, 37.4), 1)
                row['resp'] = random.uniform(12, 20)
                row['walk'] = random.randint(4000, 6000)
                row['loc_x'], row['loc_y'] = random_location()
                sample = acc_gyr_df[acc_gyr_df['label'] == fall_label].sample(1).iloc[0]
                row['acc_x'] = sample['acc_x']
                row['acc_y'] = sample['acc_y']
                row['acc_z'] = sample['acc_z']
                row['gyro_x'] = sample['gyro_x']
                row['gyro_y'] = sample['gyro_y']
                row['gyro_z'] = sample['gyro_z']
                row = attach_health_info_and_profile(row['emp_id'], row)
                row['fall_label'] = sample['label']
                dummy_rows.append(row)

            senior_ids = []
            for emp_id in emp_ids[2:]:
                profile = Employee.query.filter_by(emp_id=emp_id).first()
                if profile and profile.age >= 60:
                    senior_ids.append(emp_id)
            heat_emp_id = senior_ids[0] if senior_ids else emp_ids[2]

            row = base_row.copy()
            row['emp_id'] = heat_emp_id
            row['battery'] = random.randint(0, 100)
            row['hr'] = 150
            row['temp'] = 40.0
            row['resp'] = 25
            row['walk'] = random.randint(4000, 6000)
            row['loc_x'], row['loc_y'] = random_location()
            sample = acc_gyr_df[acc_gyr_df['label'].isin(labels_normal)].sample(1).iloc[0]
            row['acc_x'] = sample['acc_x']
            row['acc_y'] = sample['acc_y']
            row['acc_z'] = sample['acc_z']
            row['gyro_x'] = sample['gyro_x']
            row['gyro_y'] = sample['gyro_y']
            row['gyro_z'] = sample['gyro_z']
            row = attach_health_info_and_profile(row['emp_id'], row)
            row['fall_label'] = sample['label']
            dummy_rows.append(row)

            normal_emp_ids = [emp for emp in emp_ids if emp not in fall_emp_ids + [heat_emp_id]]
            for emp_id in normal_emp_ids:
                row = base_row.copy()
                row['emp_id'] = emp_id
                row['battery'] = random.randint(20, 100)
                row['hr'] = random.uniform(60, 90)
                row['temp'] = round(random.uniform(36.2, 37.0), 1)
                row['resp'] = random.uniform(13, 18)
                row['walk'] = random.randint(4000, 6000)
                row['loc_x'], row['loc_y'] = random_location()
                sample = acc_gyr_df[acc_gyr_df['label'].isin(labels_normal)].sample(1).iloc[0]
                row['acc_x'] = sample['acc_x']
                row['acc_y'] = sample['acc_y']
                row['acc_z'] = sample['acc_z']
                row['gyro_x'] = sample['gyro_x']
                row['gyro_y'] = sample['gyro_y']
                row['gyro_z'] = sample['gyro_z']
                row = attach_health_info_and_profile(row['emp_id'], row)
                row['fall_label'] = sample['label']
                dummy_rows.append(row)

            df_all = pd.DataFrame([base_row] + dummy_rows)
            df_all = df_all.replace([np.inf, -np.inf], np.nan).fillna(0)

            bt_bins = [0, 36.0, 37.5, float('inf')]
            bt_labels = [0, 1, 2]
            df_all['temp_cat'] = pd.cut(df_all['temp'], bins=bt_bins, labels=bt_labels)

            rr_bins = [0, 11, 20, float('inf')]
            rr_labels = [0, 1, 2]
            df_all['resp_cat'] = pd.cut(df_all['resp'], bins=rr_bins, labels=rr_labels)

            hr_bins = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
            hr_labels = [0, 1, 2, 3, 4]
            df_all['hr_ratio'] = df_all['hr'] / (220 - df_all['age'])
            df_all['hr_cat'] = pd.cut(df_all['hr_ratio'], bins=hr_bins, labels=hr_labels, right=False)

            heat_cols = ['gender', 'age', 'location', 'HT', 'HeartDisease', 'Pscyco',
                         'DM', 'CerevD', 'CKD', 'hr', 'temp', 'resp']
            X_heat = df_all[heat_cols].astype(np.float32)

            ML_MODEL_PATH = os.environ.get('ML_MODEL_PATH', '/root/proj/MindPark/backend/app/mobile/service/models/heat_illness_model.h5')
            heat_model = tf.keras.models.load_model(ML_MODEL_PATH)
            heat_preds = heat_model.predict(X_heat)

            results = []
            for i in range(len(df_all)):
                measurement_id = f"M{uuid.uuid4().hex[:12]}"

                heat_prob = heat_preds[i][0]
                if heat_prob >= 0.85:
                    heat_risk = "위험"
                elif heat_prob >= 0.6:
                    heat_risk = "주의"
                else:
                    heat_risk = "정상"

                fall_label = df_all.loc[i, 'fall_label'] if 'fall_label' in df_all.columns else ''
                if fall_label in ['fall', 'lfall', 'rfall']:
                    fall_risk = "위험"
                elif fall_label == 'light':
                    fall_risk = "주의"
                else:
                    fall_risk = "정상"

                result_row = {
                    "emp_id": df_all.loc[i, "emp_id"],
                    "heat_risk": heat_risk,
                    "fall_risk": fall_risk
                }
                results.append(result_row)

                dm = DeviceMeasurement(
                    measurement_id=measurement_id,
                    emp_id=df_all.loc[i, "emp_id"],
                    device_id=df_all.loc[i, "device_id"],
                    measure_time=measure_time,
                    battery=df_all.loc[i, "battery"],
                    hr=df_all.loc[i, "hr"],
                    temp=df_all.loc[i, "temp"],
                    resp=df_all.loc[i, "resp"],
                    spo2=df_all.loc[i, "spo2"],
                    walk=df_all.loc[i, "walk"],
                    acc_x=df_all.loc[i, "acc_x"],
                    acc_y=df_all.loc[i, "acc_y"],
                    acc_z=df_all.loc[i, "acc_z"],
                    gyro_x=df_all.loc[i, "gyro_x"],
                    gyro_y=df_all.loc[i, "gyro_y"],
                    gyro_z=df_all.loc[i, "gyro_z"],
                    loc_x=df_all.loc[i, "loc_x"],
                    loc_y=df_all.loc[i, "loc_y"],
                    heat_risk=heat_risk,
                    fall_risk=fall_risk
                )
                db.session.add(dm)

                if heat_risk in ['주의', '위험']:
                    anomaly = HealthAnomaly(
                        anomaly_id=f"A{uuid.uuid4().hex[:8]}",
                        emp_id=df_all.loc[i, "emp_id"],
                        anomaly_time=measure_time,
                        symptom="온열질환",
                        risk=heat_risk,
                        status="처리중",
                        loc_x=df_all.loc[i, "loc_x"],
                        loc_y=df_all.loc[i, "loc_y"],
                        updated_at=measure_time
                    )
                    db.session.add(anomaly)

                if fall_risk in ['주의', '위험']:
                    anomaly = HealthAnomaly(
                        anomaly_id=f"A{uuid.uuid4().hex[:8]}",
                        emp_id=df_all.loc[i, "emp_id"],
                        anomaly_time=measure_time,
                        symptom="낙상",
                        risk=fall_risk,
                        status="처리중",
                        loc_x=df_all.loc[i, "loc_x"],
                        loc_y=df_all.loc[i, "loc_y"],
                        updated_at=measure_time
                    )
                    db.session.add(anomaly)

            db.session.commit()

            user_heat_result = next((res for res in results if res["emp_id"] == current_user), None)
            user_heat_status = user_heat_result["heat_risk"] if user_heat_result else "정상"

            return {
                "status": "success",
                "message": f"측정 데이터 1개가 처리되었습니다",
                "device_id": device.device_id,
                "results": [user_heat_result] if user_heat_result else [],
                "user_heat_alert": user_heat_status
            }

        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": f"서비스 처리 중 오류: {str(e)}"}
