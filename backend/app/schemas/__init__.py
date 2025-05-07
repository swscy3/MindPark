# 스키마 통합 임포트
from app.schemas.auth import SignupSchema, LoginSchema, TokenSchema
from app.schemas.employee import (
    EmployeeSchema, EmployeeUpdateSchema, EmployeeHealthSchema,
    EmergencyContactSchema, EmployeeProfileSchema, AdminSchema
)
from app.schemas.device import (
    DeviceSchema, DeviceCreateSchema, DeviceUpdateSchema,
    DeviceManagementSchema, DeviceAssignmentSchema,
    DeviceFailureSchema, DeviceFailureCreateSchema
)
from app.schemas.measurement import (
    DeviceMeasurementSchema, DeviceMeasurementCreateSchema,
    HealthAnomalySchema, HealthAnomalyCreateSchema,
    HeaderInfoSchema, HeatIncidentSchema, FallIncidentSchema,
    IncidentTotalSchema, DeviceStatusSchema, WeeklyHeatStatsSchema
)