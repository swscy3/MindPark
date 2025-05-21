from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime

class LoginSchema(Schema):
    id = fields.String(required=True, validate=validate.Length(min=1, max=10))
    password = fields.String(required=True, validate=validate.Length(min=4, max=64))
    device_name = fields.String(required=False)  # 선택적 필드 추가