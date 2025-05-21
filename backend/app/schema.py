from marshmallow import Schema, fields, validate, validates, ValidationError
from datetime import datetime

# ============================================================================
# 인증 관련 스키마
# ============================================================================

class LoginSchema(Schema):
    id = fields.String(required=True, validate=validate.Length(min=1, max=10))
    password = fields.String(required=True, validate=validate.Length(min=4, max=12))  # YYYYMMDD