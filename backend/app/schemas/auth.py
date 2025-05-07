from marshmallow import Schema, fields, validate

class SignupSchema(Schema):
    emp_id = fields.String(required=True, validate=validate.Length(min=1, max=10))
    emp_name = fields.String(required=True)
    emp_phoneNumber = fields.String(required=True)
    department = fields.String(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))

class LoginSchema(Schema):
    id = fields.String(required=True)
    password = fields.String(required=True)

class TokenSchema(Schema):
    token = fields.String()
    message = fields.String()