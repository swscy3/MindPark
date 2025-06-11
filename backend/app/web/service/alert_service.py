# app/web/services/alert_service.py
from datetime import datetime
from app import db
from app.model import HealthAnomaly
from app.util.time_utils import to_korea_time

class AlertService:
    @staticmethod
    def get_all_anomalies():
        """전체 건강 이상 데이터 조회 및 포맷팅"""
        try:
            all_anomalies = HealthAnomaly.query.options(db.joinedload(HealthAnomaly.employee)).all()
            
            formatted_data = []
            for anomaly in all_anomalies:
                employee_name = anomaly.employee.name if anomaly.employee else '알 수 없음'
                
                formatted_item = {
                    'anomaly_id': anomaly.anomaly_id,
                    'emp_id': anomaly.emp_id,
                    'emp_name': employee_name,
                    'symptom': anomaly.symptom,
                    'location': {
                        'x': anomaly.loc_x,
                        'y': anomaly.loc_y
                    },
                    'anomaly_time': to_korea_time(anomaly.anomaly_time),
                    'status': anomaly.status,
                    'management': {
                        'risk': anomaly.risk,
                        'action_content': anomaly.action_content,
                        'updated_at': to_korea_time(anomaly.updated_at)
                    }
                }
                formatted_data.append(formatted_item)
            
            return formatted_data
        except Exception as e:
            print(f"[ERROR] 건강 이상 데이터 조회 오류: {str(e)}")
            raise e

    @staticmethod
    def get_anomaly_by_id(anomaly_id):
        """특정 건강 이상 데이터 조회"""
        try:
            anomaly = HealthAnomaly.query.options(db.joinedload(HealthAnomaly.employee)).filter_by(anomaly_id=anomaly_id).first()
            
            if not anomaly:
                return None
            
            employee_name = anomaly.employee.name if anomaly.employee else '알 수 없음'
            
            return {
                'anomaly_id': anomaly.anomaly_id,
                'emp_id': anomaly.emp_id,
                'emp_name': employee_name,
                'symptom': anomaly.symptom,
                'anomaly_time': to_korea_time(anomaly.anomaly_time),
                'status': anomaly.status,
                'action_content': anomaly.action_content,
                'risk': anomaly.risk,
                'updated_at': to_korea_time(anomaly.updated_at)
            }
        except Exception as e:
            print(f"[ERROR] 건강 이상 데이터 조회 오류 (anomaly_id: {anomaly_id}): {str(e)}")
            raise e

    @staticmethod
    def update_anomaly(anomaly_id, status=None, action_content=None, current_user=None):
        """건강 이상 데이터 업데이트"""
        try:
            # 유효성 검사
            if status is not None:
                valid_statuses = ['처리중', '완료']
                if status not in valid_statuses:
                    raise ValueError(f'유효하지 않은 상태입니다. 유효한 값: {", ".join(valid_statuses)}')
            
            # 데이터베이스에서 항목 조회
            anomaly = HealthAnomaly.query.filter_by(anomaly_id=anomaly_id).first()
            if not anomaly:
                return None
            
            # 데이터 업데이트
            if status is not None:
                anomaly.status = status
            if action_content is not None:
                anomaly.action_content = action_content
            
            anomaly.updated_at = datetime.utcnow()
            db.session.commit()
            
            # 업데이트된 데이터 반환
            updated_anomaly = HealthAnomaly.query.options(db.joinedload(HealthAnomaly.employee)).filter_by(anomaly_id=anomaly_id).first()
            
            return {
                'updated_item': {
                    'anomaly_id': updated_anomaly.anomaly_id,
                    'status': updated_anomaly.status,
                    'action_content': updated_anomaly.action_content,
                    'updated_at': to_korea_time(updated_anomaly.updated_at),
                    'updated_by': current_user
                },
                'all_anomalies': AlertService.get_all_anomalies()
            }
            
        except Exception as e:
            db.session.rollback()
            print(f"[ERROR] 건강 이상 데이터 수정 오류 (anomaly_id: {anomaly_id}): {str(e)}")
            raise e