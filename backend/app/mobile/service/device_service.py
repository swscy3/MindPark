from datetime import datetime
import uuid
import pandas as pd
import numpy as np
import requests
import random

from ...model import DeviceMeasurement, DeviceManagement, EmployeeHealth, Employee
from ... import db

# acc_gyr 데이터 로딩 (전역에서 한 번만)
acc_gyr_df = pd.read_csv("/root/MindPark/backend/app/mobile/service/acc_gyr.csv")

class DeviceService:
    @staticmethod
    def process_measurement(current_user, device, data):
        try:
            # 측정 ID 및 현재 시각 생성 (날짜는 고정, 시간은 현재 시간)
            fixed_date = "20250528"
            current_time = datetime.now()
            time_part = current_time.strftime("%H%M%S")
            measurement_id = f"M{fixed_date}{time_part}{str(uuid.uuid4())[:4]}"

            # 실측 데이터 1행
            base_row = {
                "emp_id": current_user,
                "device_id": device.device_id,
                "battery": data.get("battery"),
                "hr": data.get("hr"),
                "temp": data.get("temp"),
                "resp": data.get("resp"),
                "spo2": data.get("spo2"),
                "walk": data.get("walk"),
                "acc_x": data.get("acc_x"),
                "acc_y": data.get("acc_y"),
                "acc_z": data.get("acc_z"),
                "gyro_x": data.get("gyro_x"),
                "gyro_y": data.get("gyro_y"),
                "gyro_z": data.get("gyro_z"),
                "loc_x": data.get("loc_x"),
                "loc_y": data.get("loc_y"),
                "measure_time": current_time.isoformat()
            }

            def attach_health_info_and_profile(emp_id, row):
                health = EmployeeHealth.query.filter_by(emp_id=emp_id).first()
                profile = Employee.query.filter_by(emp_id=emp_id).first()

                # 건강 정보
                row['HT'] = health.HT if health else False
                row['HeartDisease'] = health.HeartDisease if health else False
                row['Pscyco'] = health.Pscyco if health else False
                row['DM'] = health.DM if health else False
                row['CerevD'] = health.CerevD if health else False
                row['CKD'] = health.CKD if health else False

                # 성별 변환: M → 0, F → 1
                if profile and profile.gender == 'M':
                    row['gender'] = 0
                elif profile and profile.gender == 'F':
                    row['gender'] = 1
                else:
                    row['gender'] = -1

                # 나이
                row['age'] = profile.age if profile else -1

                # 위치 고정값
                row['location'] = 1
                return row

            base_row = attach_health_info_and_profile(current_user, base_row)

            emp_ids = db.session.query(DeviceManagement.emp_id).distinct().all()
            emp_ids = [emp[0] for emp in emp_ids if emp[0] != current_user]
            if len(emp_ids) < 6:
                return {"status": "error", "message": "더미 생성을 위한 충분한 emp_id가 없습니다."}
            random.shuffle(emp_ids)

            dummy_rows = []
            labels_normal = ['light', 'sit', 'step', 'walk']
            labels_abnormal = ['fall', 'lfall', 'rfall']

            for i in range(4):
                row = base_row.copy()
                row['emp_id'] = emp_ids[i]
                row['battery'] = random.randint(0, 100)
                row['hr'] = random.uniform(100, 120)
                row['temp'] = random.uniform(38, 39.5)
                row['resp'] = random.uniform(22, 28)
                label_sample = acc_gyr_df[acc_gyr_df['label'].isin(labels_normal)].sample(1).iloc[0]
                row['acc_x'] = label_sample['acc_x']
                row['acc_y'] = label_sample['acc_y']
                row['acc_z'] = label_sample['acc_z']
                row['gyro_x'] = label_sample['gyro_x']
                row['gyro_y'] = label_sample['gyro_y']
                row['gyro_z'] = label_sample['gyro_z']
                row['walk'] = random.randint(300, 400)
                row = attach_health_info_and_profile(row['emp_id'], row)
                dummy_rows.append(row)

            for i in range(4, 6):
                row = base_row.copy()
                row['emp_id'] = emp_ids[i]
                row['battery'] = random.randint(0, 100)
                row['hr'] = random.uniform(60, 99)
                row['temp'] = random.uniform(35.6, 37.4)
                row['resp'] = random.uniform(12, 20)
                row['walk'] = random.randint(0, 300)
                label_sample = acc_gyr_df[acc_gyr_df['label'].isin(labels_abnormal)].sample(1).iloc[0]
                row['acc_x'] = label_sample['acc_x']
                row['acc_y'] = label_sample['acc_y']
                row['acc_z'] = label_sample['acc_z']
                row['gyro_x'] = label_sample['gyro_x']
                row['gyro_y'] = label_sample['gyro_y']
                row['gyro_z'] = label_sample['gyro_z']
                row['walk'] = random.randint(300, 400)
                row = attach_health_info_and_profile(row['emp_id'], row)
                dummy_rows.append(row)

            for _ in range(73):
                row = base_row.copy()
                row['battery'] = random.randint(0, 100)
                row['hr'] = random.uniform(60, 99)
                row['temp'] = random.uniform(35.6, 37.4)
                row['resp'] = random.uniform(12, 20)
                label_sample = acc_gyr_df[acc_gyr_df['label'].isin(labels_normal)].sample(1).iloc[0]
                row['acc_x'] = label_sample['acc_x']
                row['acc_y'] = label_sample['acc_y']
                row['acc_z'] = label_sample['acc_z']
                row['gyro_x'] = label_sample['gyro_x']
                row['gyro_y'] = label_sample['gyro_y']
                row['gyro_z'] = label_sample['gyro_z']
                row['walk'] = random.randint(300, 400)
                row = attach_health_info_and_profile(current_user, row)
                dummy_rows.append(row)

            # 전체 데이터 병합 (base_row 포함하지 않음)
            df_all = pd.DataFrame([base_row] + dummy_rows)

            # 💡 NaN 또는 무한대 값 제거
            df_all = df_all.replace([np.inf, -np.inf], np.nan)
            df_all = df_all.fillna(0)

            json_data = df_all.to_dict(orient='records')

            try:
                gpu_response = requests.post("http://localhost:8000/gpu/predict", json={"records": json_data})
                gpu_result = gpu_response.json()
            except Exception as e:
                return {"status": "error", "message": f"GPU 서버 오류: {str(e)}"}

            return {
                "status": "success",
                "message": f"측정 데이터 {len(json_data)}개가 처리되었습니다",
                "measurement_id": measurement_id,
                "device_id": device.device_id,
                "gpu_result": gpu_result
            }

        except Exception as e:
            return {"status": "error", "message": f"서비스 처리 중 오류: {str(e)}"}
