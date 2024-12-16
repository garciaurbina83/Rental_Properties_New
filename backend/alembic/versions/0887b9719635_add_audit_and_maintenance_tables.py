"""add_audit_and_maintenance_tables

Revision ID: 0887b9719635
Revises: e282eea5d59a
Create Date: 2024-12-03 10:45:36.623156

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0887b9719635'
down_revision = 'e282eea5d59a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Eliminar tablas existentes si existen
    op.execute("DROP TABLE IF EXISTS maintenance_attachments CASCADE")
    op.execute("DROP TABLE IF EXISTS maintenance_requests CASCADE")
    op.execute("DROP TABLE IF EXISTS audit_log CASCADE")

    # Crear enum para estados de mantenimiento
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    existing_enums = inspector.get_enums()
    existing_enum_names = [enum['name'] for enum in existing_enums]
    
    if 'maintenance_status' not in existing_enum_names:
        op.execute("CREATE TYPE maintenance_status AS ENUM ('pending', 'in_progress', 'completed')")
    if 'maintenance_priority' not in existing_enum_names:
        op.execute("CREATE TYPE maintenance_priority AS ENUM ('low', 'medium', 'high', 'urgent')")

    # Crear tabla audit_log
    op.create_table(
        'audit_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('entity_type', sa.String(), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('changes', sa.JSON(), nullable=True),
        sa.Column('performed_by', sa.Integer(), nullable=False),
        sa.Column('performed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('ip_address', sa.String(), nullable=True),
        sa.Column('user_agent', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['performed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_audit_log_entity_type'), 'audit_log', ['entity_type'], unique=False)

    # Crear tabla maintenance_requests
    op.create_table(
        'maintenance_requests',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('property_id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('priority', sa.String(), nullable=False, server_default='medium'),
        sa.Column('request_date', sa.Date(), nullable=False),
        sa.Column('scheduled_date', sa.Date(), nullable=True),
        sa.Column('completion_date', sa.Date(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('actual_cost', sa.Float(), nullable=True),
        sa.Column('work_performed', sa.String(), nullable=True),
        sa.Column('contractor_info', sa.String(), nullable=True),
        sa.Column('invoice_number', sa.String(), nullable=True),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('photos_path', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla maintenance_attachments
    op.create_table(
        'maintenance_attachments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('maintenance_request_id', sa.Integer(), nullable=False),
        sa.Column('file_name', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('file_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('description', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['maintenance_request_id'], ['maintenance_requests.id'], ),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('maintenance_attachments')
    op.drop_table('maintenance_requests')
    op.drop_table('audit_log')
    op.execute('DROP TYPE maintenance_status')
    op.execute('DROP TYPE maintenance_priority')
