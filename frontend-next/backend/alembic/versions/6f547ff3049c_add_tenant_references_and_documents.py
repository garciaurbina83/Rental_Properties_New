"""add_tenant_references_and_documents

Revision ID: 6f547ff3049c
Revises: 5fa6c40413c1
Create Date: 2024-11-30 00:42:24.144874

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6f547ff3049c'
down_revision = '5fa6c40413c1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create enum types first
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'unittype') THEN CREATE TYPE unittype AS ENUM ('APARTMENT', 'HOUSE', 'ROOM', 'OFFICE', 'RETAIL', 'WAREHOUSE', 'OTHER'); END IF; END $$")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'maintenancestatus') THEN CREATE TYPE maintenancestatus AS ENUM ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'); END IF; END $$")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'maintenancepriority') THEN CREATE TYPE maintenancepriority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT'); END IF; END $$")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'paymentfrequency') THEN CREATE TYPE paymentfrequency AS ENUM ('MONTHLY', 'BIMONTHLY', 'QUARTERLY', 'SEMIANNUAL', 'ANNUAL'); END IF; END $$")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'expensetype') THEN CREATE TYPE expensetype AS ENUM ('MAINTENANCE', 'UTILITIES', 'TAXES', 'INSURANCE', 'MORTGAGE', 'IMPROVEMENTS', 'MANAGEMENT', 'LEGAL', 'OTHER'); END IF; END $$")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'contactmethod') THEN CREATE TYPE contactmethod AS ENUM ('EMAIL', 'PHONE', 'WHATSAPP'); END IF; END $$")
    op.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tenantstatus') THEN CREATE TYPE tenantstatus AS ENUM ('ACTIVE', 'INACTIVE', 'PENDING', 'BLACKLISTED'); END IF; END $$")
    
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tenant_documents',
    sa.Column('tenant_id', sa.Integer(), nullable=True),
    sa.Column('document_type', sa.String(), nullable=True),
    sa.Column('file_path', sa.String(), nullable=True),
    sa.Column('upload_date', sa.Date(), nullable=True),
    sa.Column('expiry_date', sa.Date(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenant_documents_id'), 'tenant_documents', ['id'], unique=False)
    op.create_table('tenant_references',
    sa.Column('tenant_id', sa.Integer(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('ref_relationship', sa.String(), nullable=True),
    sa.Column('phone', sa.String(), nullable=True),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenant_references_id'), 'tenant_references', ['id'], unique=False)
    op.create_table('units',
    sa.Column('property_id', sa.Integer(), nullable=True),
    sa.Column('unit_number', sa.String(), nullable=True),
    sa.Column('floor', sa.Integer(), nullable=True),
    sa.Column('unit_type', postgresql.ENUM('APARTMENT', 'HOUSE', 'ROOM', 'OFFICE', 'RETAIL', 'WAREHOUSE', 'OTHER', name='unittype', create_type=False), nullable=True),
    sa.Column('bedrooms', sa.Integer(), nullable=True),
    sa.Column('bathrooms', sa.Float(), nullable=True),
    sa.Column('total_area', sa.Float(), nullable=True),
    sa.Column('furnished', sa.Boolean(), nullable=True),
    sa.Column('is_available', sa.Boolean(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('base_rent', sa.Float(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('amenities', sa.String(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_units_id'), 'units', ['id'], unique=False)
    op.create_table('maintenance_requests',
    sa.Column('property_id', sa.Integer(), nullable=True),
    sa.Column('unit_id', sa.Integer(), nullable=True),
    sa.Column('tenant_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('status', postgresql.ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', name='maintenancestatus', create_type=False), nullable=True),
    sa.Column('priority', postgresql.ENUM('LOW', 'MEDIUM', 'HIGH', 'URGENT', name='maintenancepriority', create_type=False), nullable=True),
    sa.Column('request_date', sa.Date(), nullable=True),
    sa.Column('scheduled_date', sa.Date(), nullable=True),
    sa.Column('completion_date', sa.Date(), nullable=True),
    sa.Column('estimated_cost', sa.Float(), nullable=True),
    sa.Column('actual_cost', sa.Float(), nullable=True),
    sa.Column('work_performed', sa.String(), nullable=True),
    sa.Column('contractor_info', sa.String(), nullable=True),
    sa.Column('invoice_number', sa.String(), nullable=True),
    sa.Column('notes', sa.String(), nullable=True),
    sa.Column('photos_path', sa.String(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_maintenance_requests_id'), 'maintenance_requests', ['id'], unique=False)
    op.create_table('contract_documents',
    sa.Column('contract_id', sa.Integer(), nullable=True),
    sa.Column('document_type', sa.String(), nullable=True),
    sa.Column('file_path', sa.String(), nullable=True),
    sa.Column('upload_date', sa.Date(), nullable=True),
    sa.Column('is_signed', sa.Boolean(), nullable=True),
    sa.Column('signed_date', sa.Date(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contract_documents_id'), 'contract_documents', ['id'], unique=False)
    op.add_column('contracts', sa.Column('unit_id', sa.Integer(), nullable=True))
    op.add_column('contracts', sa.Column('contract_number', sa.String(), nullable=True))
    op.add_column('contracts', sa.Column('rent_amount', sa.Float(), nullable=True))
    op.add_column('contracts', sa.Column('payment_frequency', postgresql.ENUM('MONTHLY', 'BIMONTHLY', 'QUARTERLY', 'SEMIANNUAL', 'ANNUAL', name='paymentfrequency', create_type=False), nullable=True))
    op.add_column('contracts', sa.Column('payment_due_day', sa.Integer(), nullable=True))
    op.add_column('contracts', sa.Column('terms_and_conditions', sa.String(), nullable=True))
    op.add_column('contracts', sa.Column('special_conditions', sa.String(), nullable=True))
    op.add_column('contracts', sa.Column('last_payment_date', sa.Date(), nullable=True))
    op.add_column('contracts', sa.Column('deposit_returned', sa.Boolean(), nullable=True))
    op.add_column('contracts', sa.Column('deposit_return_date', sa.Date(), nullable=True))
    op.add_column('contracts', sa.Column('deposit_deductions', sa.Float(), nullable=True))
    op.add_column('contracts', sa.Column('deposit_notes', sa.String(), nullable=True))
    op.add_column('contracts', sa.Column('is_renewable', sa.Boolean(), nullable=True))
    op.add_column('contracts', sa.Column('renewal_price_increase', sa.Float(), nullable=True))
    op.add_column('contracts', sa.Column('auto_renewal', sa.Boolean(), nullable=True))
    op.create_unique_constraint(None, 'contracts', ['contract_number'])
    op.drop_constraint('contracts_property_id_fkey', 'contracts', type_='foreignkey')
    op.create_foreign_key(None, 'contracts', 'units', ['unit_id'], ['id'])
    op.drop_column('contracts', 'payment_day')
    op.drop_column('contracts', 'property_id')
    op.drop_column('contracts', 'late_fee_percentage')
    op.drop_column('contracts', 'monthly_rent')
    op.drop_column('contracts', 'is_active')
    op.add_column('expenses', sa.Column('unit_id', sa.Integer(), nullable=True))
    op.add_column('expenses', sa.Column('expense_type', postgresql.ENUM('MAINTENANCE', 'UTILITIES', 'TAXES', 'INSURANCE', 'MORTGAGE', 'IMPROVEMENTS', 'MANAGEMENT', 'LEGAL', 'OTHER', name='expensetype', create_type=False), nullable=True))
    op.add_column('expenses', sa.Column('date_incurred', sa.Date(), nullable=True))
    op.add_column('expenses', sa.Column('payment_method', sa.String(), nullable=True))
    op.add_column('expenses', sa.Column('reference_number', sa.String(), nullable=True))
    op.add_column('expenses', sa.Column('notes', sa.String(), nullable=True))
    op.add_column('expenses', sa.Column('receipt_path', sa.String(), nullable=True))
    op.drop_constraint('expenses_maintenance_ticket_id_fkey', 'expenses', type_='foreignkey')
    op.create_foreign_key(None, 'expenses', 'units', ['unit_id'], ['id'])
    op.drop_column('expenses', 'invoice_number')
    op.drop_column('expenses', 'category')
    op.drop_column('expenses', 'maintenance_ticket_id')
    op.drop_column('expenses', 'receipt_url')
    op.add_column('properties', sa.Column('postal_code', sa.String(), nullable=True))
    op.add_column('properties', sa.Column('total_area', sa.Float(), nullable=True))
    op.add_column('properties', sa.Column('floors', sa.Integer(), nullable=True))
    op.add_column('properties', sa.Column('monthly_expenses', sa.Float(), nullable=True))
    op.add_column('properties', sa.Column('purchase_date', sa.Date(), nullable=True))
    op.add_column('tenants', sa.Column('occupation', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('monthly_income', sa.Float(), nullable=True))
    op.add_column('tenants', sa.Column('previous_address', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('preferred_contact_method', postgresql.ENUM('EMAIL', 'PHONE', 'WHATSAPP', name='contactmethod', create_type=False), nullable=True))
    op.add_column('tenants', sa.Column('notes', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('date_of_birth', sa.Date(), nullable=True))
    op.add_column('tenants', sa.Column('employer', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('status', postgresql.ENUM('ACTIVE', 'INACTIVE', 'PENDING', 'BLACKLISTED', name='tenantstatus', create_type=False), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tenants', 'status')
    op.drop_column('tenants', 'employer')
    op.drop_column('tenants', 'date_of_birth')
    op.drop_column('tenants', 'notes')
    op.drop_column('tenants', 'preferred_contact_method')
    op.drop_column('tenants', 'previous_address')
    op.drop_column('tenants', 'monthly_income')
    op.drop_column('tenants', 'occupation')
    op.drop_column('properties', 'purchase_date')
    op.drop_column('properties', 'monthly_expenses')
    op.drop_column('properties', 'floors')
    op.drop_column('properties', 'total_area')
    op.drop_column('properties', 'postal_code')
    op.add_column('expenses', sa.Column('receipt_url', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('expenses', sa.Column('maintenance_ticket_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('expenses', sa.Column('category', postgresql.ENUM('MAINTENANCE', 'UTILITIES', 'TAXES', 'INSURANCE', 'MORTGAGE', 'OTHER', name='expensecategory'), autoincrement=False, nullable=True))
    op.add_column('expenses', sa.Column('invoice_number', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'expenses', type_='foreignkey')
    op.create_foreign_key('expenses_maintenance_ticket_id_fkey', 'expenses', 'maintenance_tickets', ['maintenance_ticket_id'], ['id'])
    op.drop_column('expenses', 'receipt_path')
    op.drop_column('expenses', 'notes')
    op.drop_column('expenses', 'reference_number')
    op.drop_column('expenses', 'payment_method')
    op.drop_column('expenses', 'date_incurred')
    op.drop_column('expenses', 'expense_type')
    op.drop_column('expenses', 'unit_id')
    op.add_column('contracts', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('contracts', sa.Column('monthly_rent', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('contracts', sa.Column('late_fee_percentage', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True))
    op.add_column('contracts', sa.Column('property_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('contracts', sa.Column('payment_day', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'contracts', type_='foreignkey')
    op.create_foreign_key('contracts_property_id_fkey', 'contracts', 'properties', ['property_id'], ['id'])
    op.drop_constraint(None, 'contracts', type_='unique')
    op.drop_column('contracts', 'auto_renewal')
    op.drop_column('contracts', 'renewal_price_increase')
    op.drop_column('contracts', 'is_renewable')
    op.drop_column('contracts', 'deposit_notes')
    op.drop_column('contracts', 'deposit_deductions')
    op.drop_column('contracts', 'deposit_return_date')
    op.drop_column('contracts', 'deposit_returned')
    op.drop_column('contracts', 'last_payment_date')
    op.drop_column('contracts', 'special_conditions')
    op.drop_column('contracts', 'terms_and_conditions')
    op.drop_column('contracts', 'payment_due_day')
    op.drop_column('contracts', 'payment_frequency')
    op.drop_column('contracts', 'rent_amount')
    op.drop_column('contracts', 'contract_number')
    op.drop_column('contracts', 'unit_id')
    op.drop_index(op.f('ix_contract_documents_id'), table_name='contract_documents')
    op.drop_table('contract_documents')
    op.drop_index(op.f('ix_maintenance_requests_id'), table_name='maintenance_requests')
    op.drop_table('maintenance_requests')
    op.drop_index(op.f('ix_units_id'), table_name='units')
    op.drop_table('units')
    op.drop_index(op.f('ix_tenant_references_id'), table_name='tenant_references')
    op.drop_table('tenant_references')
    op.drop_index(op.f('ix_tenant_documents_id'), table_name='tenant_documents')
    op.drop_table('tenant_documents')
    # Drop enum types
    op.execute("DROP TYPE IF EXISTS unittype")
    op.execute("DROP TYPE IF EXISTS maintenancestatus")
    op.execute("DROP TYPE IF EXISTS maintenancepriority")
    op.execute("DROP TYPE IF EXISTS paymentfrequency")
    op.execute("DROP TYPE IF EXISTS expensetype")
    op.execute("DROP TYPE IF EXISTS contactmethod")
    op.execute("DROP TYPE IF EXISTS tenantstatus")
    # ### end Alembic commands ###
