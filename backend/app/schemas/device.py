from marshmallow import Schema, fields, validate
from datetime import datetime

class DeviceSchema(Schema):
    device_id = fields.String()
    product = fields.String()
    manager_id = fields.String()

class DeviceCreateSchema(Schema):
    product = fields.String(required=True)
    manager_id = fields.String(required=True)

class DeviceUpdateSchema(Schema):
    product = fields.String()
    manager_id = fields.String()

class DeviceManagementSchema(Schema):
    device_id = fields.String()
    emp_id = fields.String()
    check_in = fields.DateTime()
    check_out = fields.DateTime()

class DeviceAssignmentSchema(Schema):
    device_id = fields.String(required=True)
    emp_id = fields.String(required=True)

class DeviceFailureSchema(Schema):
    fail_id = fields.String()
    device_id = fields.String()
    emp_id = fields.String()
    fail_time = fields.DateTime()
    reason = fields.String()

class DeviceFailureCreateSchema(Schema):
    device_id = fields.String(required=True)
    emp_id = fields.String(required=True)
    reason = fields.String(required=True)