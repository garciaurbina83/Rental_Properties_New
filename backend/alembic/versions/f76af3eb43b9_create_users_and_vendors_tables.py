"""create_users_and_vendors_tables

Revision ID: f76af3eb43b9
Revises: 2024_01_add_vendors
Create Date: 2024-01-09 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f76af3eb43b9'
down_revision = '2024_01_add_vendors'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create vendors table
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('contact_person', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('phone', sa.String(), nullable=True),
        sa.Column('address', sa.String(), nullable=True),
        sa.Column('tax_id', sa.String(), nullable=True),
        sa.Column('services', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('rating', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='active'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.UniqueConstraint('email')
    )
    op.create_index(op.f('ix_vendors_id'), 'vendors', ['id'], unique=False)
    op.create_index(op.f('ix_vendors_name'), 'vendors', ['name'], unique=False)

    # Drop and recreate expenses table with updated schema
    op.drop_table('expenses')
    op.create_table(
        'expenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('property_id', sa.Integer(), nullable=False),
        sa.Column('unit_id', sa.Integer(), nullable=True),
        sa.Column('maintenance_ticket_id', sa.Integer(), nullable=True),
        sa.Column('vendor_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.String(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('expense_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='draft'),
        sa.Column('date_incurred', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=True),
        sa.Column('payment_date', sa.Date(), nullable=True),
        sa.Column('payment_method', sa.String(), nullable=True),
        sa.Column('reference_number', sa.String(), nullable=True),
        sa.Column('requires_approval', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('approved_at', sa.Date(), nullable=True),
        sa.Column('rejection_reason', sa.String(), nullable=True),
        sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('recurrence_interval', sa.String(), nullable=True),
        sa.Column('recurrence_end_date', sa.Date(), nullable=True),
        sa.Column('parent_expense_id', sa.Integer(), nullable=True),
        sa.Column('attachments', sa.JSON(), nullable=True),
        sa.Column('receipt_path', sa.String(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['property_id'], ['properties.id'], ),
        sa.ForeignKeyConstraint(['unit_id'], ['units.id'], ),
        sa.ForeignKeyConstraint(['maintenance_ticket_id'], ['maintenance_tickets.id'], ),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id'], ),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['parent_expense_id'], ['expenses.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], )
    )
    op.create_index(op.f('ix_expenses_id'), 'expenses', ['id'], unique=False)


def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_expenses_id'), table_name='expenses')
    op.drop_index(op.f('ix_vendors_name'), table_name='vendors')
    op.drop_index(op.f('ix_vendors_id'), table_name='vendors')
    op.drop_index(op.f('ix_users_id'), table_name='users')

    # Drop tables in reverse order
    op.drop_table('expenses')
    op.drop_table('vendors')
    op.drop_table('users')
