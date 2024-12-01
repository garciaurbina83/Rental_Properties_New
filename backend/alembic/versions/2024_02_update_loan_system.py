"""update loan system

Revision ID: 2024_02_update_loan
Revises: 2024_01_add_vendors_and_update_expenses
Create Date: 2024-02-07

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_02_update_loan'
down_revision = '2024_01_add_vendors_and_update_expenses'
branch_labels = None
depends_on = None

def upgrade():
    # Crear enum types
    op.execute("CREATE TYPE loan_type AS ENUM ('mortgage', 'renovation', 'equity', 'personal', 'business', 'other')")
    op.execute("CREATE TYPE loan_status AS ENUM ('active', 'paid', 'default', 'refinanced', 'pending')")
    op.execute("CREATE TYPE payment_method AS ENUM ('cash', 'transfer', 'check', 'card')")
    op.execute("CREATE TYPE payment_status AS ENUM ('pending', 'completed', 'failed', 'cancelled')")

    # Modificar tabla loans existente
    op.add_column('loans', sa.Column('payment_day', sa.Integer(), nullable=True))
    op.add_column('loans', sa.Column('last_payment_date', sa.Date(), nullable=True))
    op.add_column('loans', sa.Column('next_payment_date', sa.Date(), nullable=True))
    op.add_column('loans', sa.Column('notes', sa.String(), nullable=True))
    
    # Crear tabla loan_documents
    op.create_table(
        'loan_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('loan_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(), nullable=False),
        sa.Column('file_path', sa.String(), nullable=False),
        sa.Column('upload_date', sa.Date(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verified_by', sa.Integer(), nullable=True),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['loan_id'], ['loans.id'], ),
        sa.ForeignKeyConstraint(['verified_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear tabla loan_payments
    op.create_table(
        'loan_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('loan_id', sa.Integer(), nullable=False),
        sa.Column('payment_date', sa.Date(), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('principal_amount', sa.Float(), nullable=False),
        sa.Column('interest_amount', sa.Float(), nullable=False),
        sa.Column('late_fee', sa.Float(), default=0.0),
        sa.Column('payment_method', postgresql.ENUM('cash', 'transfer', 'check', 'card', name='payment_method'), nullable=False),
        sa.Column('reference_number', sa.String(), nullable=True),
        sa.Column('status', postgresql.ENUM('pending', 'completed', 'failed', 'cancelled', name='payment_status'), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('processed_by', sa.Integer(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['loan_id'], ['loans.id'], ),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Crear índices
    op.create_index(op.f('ix_loan_documents_loan_id'), 'loan_documents', ['loan_id'], unique=False)
    op.create_index(op.f('ix_loan_payments_loan_id'), 'loan_payments', ['loan_id'], unique=False)
    op.create_index(op.f('ix_loan_payments_payment_date'), 'loan_payments', ['payment_date'], unique=False)
    op.create_index(op.f('ix_loan_payments_due_date'), 'loan_payments', ['due_date'], unique=False)
    op.create_index(op.f('ix_loan_payments_status'), 'loan_payments', ['status'], unique=False)

def downgrade():
    # Eliminar índices
    op.drop_index(op.f('ix_loan_payments_status'), table_name='loan_payments')
    op.drop_index(op.f('ix_loan_payments_due_date'), table_name='loan_payments')
    op.drop_index(op.f('ix_loan_payments_payment_date'), table_name='loan_payments')
    op.drop_index(op.f('ix_loan_payments_loan_id'), table_name='loan_payments')
    op.drop_index(op.f('ix_loan_documents_loan_id'), table_name='loan_documents')

    # Eliminar tablas
    op.drop_table('loan_payments')
    op.drop_table('loan_documents')

    # Eliminar columnas añadidas a loans
    op.drop_column('loans', 'notes')
    op.drop_column('loans', 'next_payment_date')
    op.drop_column('loans', 'last_payment_date')
    op.drop_column('loans', 'payment_day')

    # Eliminar enum types
    op.execute('DROP TYPE payment_status')
    op.execute('DROP TYPE payment_method')
    op.execute('DROP TYPE loan_status')
    op.execute('DROP TYPE loan_type')
