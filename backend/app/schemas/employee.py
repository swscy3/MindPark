from marshmallow import Schema, fields, validate

class EmployeeSchema(Schema):
    emp_id = fields.String()
    name = fields.String()
    dept = fields.String()
    position = fields.String()
    phone = fields.String()
    email = fields.String()
    addr = fields.String()
    birth = fields.Date()
    gender = fields.String()
    age = fields.Integer()

class EmployeeUpdateSchema(Schema):
    name = fields.String()
    dept = fields.String()
    position = fields.String()
    phone = fields.String()
    email = fields.String()
    addr = fields.String()
    birth = fields.Date()
    gender = fields.String()
    age = fields.Integer()

class EmployeeHealthSchema(Schema):
    emp_id = fields.String()
    HT = fields.Boolean()
    HeartDisease = fields.Boolean()
    Pscyco = fields.Boolean()
    DM = fields.Boolean()
    CerevD = fields.Boolean()
    CKD = fields.Boolean()

class EmergencyContactSchema(Schema):
    emp_id = fields.String()
    contact_name = fields.String()
    relation = fields.String()
    contact_phone = fields.String()

class EmployeeProfileSchema(Schema):
    employee = fields.Nested(EmployeeSchema)
    health = fields.Nested(EmployeeHealthSchema)
    emergency_contact = fields.Nested(EmergencyContactSchema)

class AdminSchema(Schema):
    admin_id = fields.String()