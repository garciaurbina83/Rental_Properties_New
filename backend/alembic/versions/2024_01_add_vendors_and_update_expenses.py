"""add vendors and update expenses

Revision ID: 2024_01_add_vendors
Revises: 6f547ff3049c
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_01_add_vendors'
down_revision = '6f547ff3049c'
branch_labels = None
depends_on = None

def upgrade():
    # Crear tabla vendors
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('business_type', sa.String(), nullable=True),
        sa.Column('tax_id', sa.String(), nullable=True),
        sa.Column('contact_person', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('website', sa.String(), nullable=True),
        sa.Column('bank_name', sa.String(), nullable=True),
        sa.Column('bank_account', sa.String(), nullable=True),
        sa.Column('payment_terms', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('rating', sa.Integer(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('documents_path', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Verificar si la tabla expenses existe
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    if 'expenses' in inspector.get_table_names():
        # Eliminar la tabla expenses existente
        op.drop_table('expenses')
    
    # Crear tabla expenses
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        # Relaciones
        sa.Column('property_id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('maintenance_ticket_id', sa.Integer(), nullable=True),
        sa.Column('vendor_id', sa.Integer(), nullable=True),
        # Información básica
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('expense_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='draft'),
        # Fechas
        sa.Column('date_incurred', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('payment_date', sa.Date(), nullable=True),
        # Detalles de pago
        sa.Column('payment_method', sa.String(), nullable=True),
        sa.Column('reference_number', sa.String(), nullable=True),
        # Sistema de aprobación
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.Date(), nullable=True),
        sa.Column('rejection_reason', sa.String(), nullable=True),
        # Gastos recurrentes
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recurrence_interval', sa.String(), nullable=True),
        sa.Column('recurrence_end_date', sa.Date(), nullable=True),
        sa.Column('parent_expense_id', sa.Integer(), nullable=True),
        # Archivos y documentación
        sa.Column('attachments', postgresql.JSONB(), nullable=True),
        sa.Column('receipt_path', sa.String(), nullable=True),
        # Notas y metadatos
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', postgresql.JSONB(), nullable=True),
        sa.Column('custom_fields', postgresql.JSONB(), nullable=True),
        # Constraints
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.ForeignKeyConstraint(['maintenance_ticket_id'], ['maintenance_tickets.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_expense_id'], ['expenses.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    )

    # Crear índices
    op.create_index(op.f('ix_vendors_name'), 'vendors', ['name'], unique=False)
    op.create_index(op.f('ix_expenses_property_id'), 'expenses', ['property_id'], unique=False)
    op.create_index(op.f('ix_expenses_vendor_id'), 'expenses', ['vendor_id'], unique=False)
    op.create_index(op.f('ix_expenses_date_incurred'), 'expenses', ['date_incurred'], unique=False)
    op.create_index(op.f('ix_expenses_status'), 'expenses', ['status'], unique=False)

def downgrade():
    # Eliminar índices
    op.drop_index(op.f('ix_vendors_name'), table_name='vendors')
    op.drop_index(op.f('ix_expenses_property_id'), table_name='expenses')
    op.drop_index(op.f('ix_expenses_vendor_id'), table_name='expenses')
    op.drop_index(op.f('ix_expenses_date_incurred'), table_name='expenses')
    op.drop_index(op.f('ix_expenses_status'), table_name='expenses')

    # Eliminar tablas
    op.drop_table('expenses')
    op.drop_table('vendors')
