from marshmallow import Schema, fields, validate

# 측정 데이터 스키마
class DeviceMeasurementSchema(Schema):
    measurement_id = fields.String()
    emp_id = fields.String()
    device_id = fields.String()
    measure_time = fields.DateTime()
    battery = fields.Integer()
    hr = fields.Integer()
    temp = fields.Float()
    resp = fields.Integer()
    spo2 = fields.Integer()
    acc_x = fields.Float()
    acc_y = fields.Float()
    acc_z = fields.Float()
    gyro_x = fields.Float()
    gyro_y = fields.Float()
    gyro_z = fields.Float()
    heat_risk = fields.Float()
    fall_risk = fields.Float()

class DeviceMeasurementCreateSchema(Schema):
    emp_id = fields.String(required=True)
    device_id = fields.String(required=True)
    battery = fields.Integer(required=True)
    hr = fields.Integer(required=True)
    temp = fields.Float(required=True)
    resp = fields.Integer()
    spo2 = fields.Integer()
    acc_x = fields.Float()
    acc_y = fields.Float()
    acc_z = fields.Float()
    gyro_x = fields.Float()
    gyro_y = fields.Float()
    gyro_z = fields.Float()
    heat_risk = fields.Float()
    fall_risk = fields.Float()

class HealthAnomalySchema(Schema):
    anomaly_id = fields.String()
    emp_id = fields.String()
    anomaly_time = fields.DateTime()
    symptom = fields.String()
    risk = fields.String()
    loc_x = fields.Float()
    loc_y = fields.Float()

class HealthAnomalyCreateSchema(Schema):
    emp_id = fields.String(required=True)
    symptom = fields.String(required=True)
    risk = fields.String(required=True)
    loc_x = fields.Float(required=True)
    loc_y = fields.Float(required=True)

# 대시보드 스키마
class HeaderInfoSchema(Schema):
    man_name = fields.String()
    man_photo = fields.String()
    site_temp = fields.Float()
    site_humi = fields.Float()
    site_wind = fields.Float()
    notice_title = fields.List(fields.String())

class HeatIncidentSchema(Schema):
    heat_name = fields.List(fields.String())
    heat_temp = fields.List(fields.String())
    heat_hr = fields.List(fields.String())
    heat_risk = fields.List(fields.String())
    heat_incident_lat = fields.List(fields.Float())
    heat_incident_lng = fields.List(fields.Float())

class FallIncidentSchema(Schema):
    fall_name = fields.List(fields.String())
    fall_temp = fields.List(fields.String())
    fall_hr = fields.List(fields.String())
    fall_state = fields.List(fields.String())
    fall_incident_lat = fields.List(fields.Float())
    fall_incident_lng = fields.List(fields.Float())

class IncidentTotalSchema(Schema):
    heat_incident_total = fields.Integer()
    fall_incident_total = fields.Integer()

class DeviceStatusSchema(Schema):
    device_total = fields.Integer()
    device_active = fields.Integer()
    device_error = fields.Integer()

class WeeklyHeatStatsSchema(Schema):
    heat_week_4 = fields.Integer()
    heat_week_3 = fields.Integer()
    heat_week_2 = fields.Integer()
    heat_week_1 = fields.Integer()
    heat_week_0 = fields.Integer()