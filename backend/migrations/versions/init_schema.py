"""initial schema migration"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'init_schema'
down_revision = None

def upgrade():
    op.create_table(
        'EMPLOYEE',
        sa.Column('emp_id', sa.String(10), primary_key=True),
        sa.Column('name', sa.String(100)),
        sa.Column('dept', sa.String(100)),
        sa.Column('position', sa.String(50)),
        sa.Column('phone', sa.String(20)),
        sa.Column('email', sa.String(100)),
        sa.Column('addr', sa.String(255)),
        sa.Column('birth', sa.Date),
        sa.Column('gender', sa.String(10)),
        sa.Column('age', sa.Integer),
        sa.Column('picture', sa.String(255)),
        sa.Column('password', sa.String(12)),
        sa.CheckConstraint("CHAR_LENGTH(password) BETWEEN 4 AND 12")
    )

    op.create_table(
        'ADMIN',
        sa.Column('admin_id', sa.String(10), sa.ForeignKey('EMPLOYEE.emp_id'), primary_key=True)
    )

    op.create_table(
        'EMPLOYEE_HEALTH',
        sa.Column('emp_id', sa.String(10), sa.ForeignKey('EMPLOYEE.emp_id'), primary_key=True),
        sa.Column('HT', sa.Boolean),
        sa.Column('HeartDisease', sa.Boolean),
        sa.Column('Pscyco', sa.Boolean),
        sa.Column('DM', sa.Boolean),
        sa.Column('CerevD', sa.Boolean),
        sa.Column('CKD', sa.Boolean),
        sa.Column('other_conditions', sa.String(255), nullable=True)
    )

    op.create_table(
        'EMERGENCY_CONTACT',
        sa.Column('emp_id', sa.String(10), sa.ForeignKey('EMPLOYEE.emp_id'), primary_key=True),
        sa.Column('contact_name', sa.String(100)),
        sa.Column('relation', sa.String(50)),
        sa.Column('contact_phone', sa.String(20))
    )

    op.create_table(
        'DEVICE',
        sa.Column('device_id', sa.String(10), primary_key=True),
        sa.Column('product', sa.String(100)),
        sa.Column('manager_id', sa.String(10), sa.ForeignKey('EMPLOYEE.emp_id')),
        sa.Column('emp_id', sa.String(10), sa.ForeignKey('EMPLOYEE.emp_id'))
    )

    op.create_table(
        'EMPLOYEE_ATTENDANCE',
        sa.Column('device_id', sa.String(10), sa.ForeignKey('DEVICE.device_id'), primary_key=True),
        sa.Column('emp_id', sa.String(10), sa.ForeignKey('EMPLOYEE.emp_id'), primary_key=True),
        sa.Column('check_in', sa.DateTime, primary_key=True),
        sa.Column('check_out', sa.DateTime)
    )

    op.create_table(
        'DEVICE_MEASUREMENT',
        sa.Column('measurement_id', sa.String(10), primary_key=True),
        sa.Column('emp_id', sa.String(10), sa.ForeignKey('EMPLOYEE.emp_id')),
        sa.Column('device_id', sa.String(10), sa.ForeignKey('DEVICE.device_id')),
        sa.Column('measure_time', sa.DateTime),
        sa.Column('battery', sa.Integer),
        sa.Column('hr', sa.Integer),
        sa.Column('temp', sa.Float),
        sa.Column('resp', sa.Integer),
        sa.Column('spo2', sa.Integer),
        sa.Column('walk', sa.Integer),
        sa.Column('acc_x', sa.Float),
        sa.Column('acc_y', sa.Float),
        sa.Column('acc_z', sa.Float),
        sa.Column('gyro_x', sa.Float),
        sa.Column('gyro_y', sa.Float),
        sa.Column('gyro_z', sa.Float),
        sa.Column('heat_risk', sa.Float),
        sa.Column('fall_risk', sa.Float)
    )

    op.create_table(
        'HEALTH_ANOMALY',
        sa.Column('anomaly_id', sa.String(10), primary_key=True),
        sa.Column('emp_id', sa.String(10), sa.ForeignKey('EMPLOYEE.emp_id')),
        sa.Column('anomaly_time', sa.DateTime),
        sa.Column('symptom', sa.String(255)),
        sa.Column('risk', sa.String(50)),
        sa.Column('status', sa.String(255)),
        sa.Column('action_content', sa.String(255)),
        sa.Column('loc_x', sa.Float),
        sa.Column('loc_y', sa.Float),
        sa.Column('updated_at', sa.DateTime)
    )

    op.create_table(
        'TOKEN_BLOCKLIST',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('jti', sa.String(36), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('expires_at', sa.DateTime, nullable=False)
    )
    op.create_index('idx_jti', 'TOKEN_BLOCKLIST', ['jti'])


def downgrade():
    op.drop_index('idx_jti', table_name='TOKEN_BLOCKLIST')
    op.drop_table('TOKEN_BLOCKLIST')
    op.drop_table('HEALTH_ANOMALY')
    op.drop_table('DEVICE_MEASUREMENT')
    op.drop_table('EMPLOYEE_ATTENDANCE')
    op.drop_table('DEVICE')
    op.drop_table('EMERGENCY_CONTACT')
    op.drop_table('EMPLOYEE_HEALTH')
    op.drop_table('ADMIN')
    op.drop_table('EMPLOYEE')
