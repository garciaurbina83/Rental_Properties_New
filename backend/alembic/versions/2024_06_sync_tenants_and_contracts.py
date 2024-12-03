"""sync tenants and contracts tables with models

Revision ID: 2024_06_sync_tenants
Revises: 2024_05_fix_property
Create Date: 2024-12-03 00:15:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2024_06_sync_tenants'
down_revision = '2024_05_fix_property'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()
    
    # 1. Actualizar tabla tenants
    try:
        # Crear nuevos tipos enum
        with connection.begin_nested():
            connection.execute(text("DROP TYPE IF EXISTS contact_method CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS tenant_status CASCADE"))
            connection.execute(text("""
                CREATE TYPE contact_method AS ENUM ('email', 'phone', 'whatsapp')
            """))
            connection.execute(text("""
                CREATE TYPE tenant_status AS ENUM ('active', 'inactive', 'pending', 'blacklisted')
            """))
            
        # Eliminar la columna si existe
        connection.execute(text("""
            ALTER TABLE tenants
            DROP COLUMN IF EXISTS preferred_contact_method,
            DROP COLUMN IF EXISTS status
        """))
        
        # Agregar las columnas con los nuevos tipos
        connection.execute(text("""
            ALTER TABLE tenants
            ADD COLUMN IF NOT EXISTS occupation VARCHAR,
            ADD COLUMN IF NOT EXISTS monthly_income FLOAT,
            ADD COLUMN IF NOT EXISTS previous_address VARCHAR,
            ADD COLUMN IF NOT EXISTS preferred_contact_method contact_method,
            ADD COLUMN IF NOT EXISTS notes VARCHAR,
            ADD COLUMN IF NOT EXISTS date_of_birth DATE,
            ADD COLUMN IF NOT EXISTS employer VARCHAR,
            ADD COLUMN IF NOT EXISTS status tenant_status
        """))
        
        # Establecer valores por defecto
        connection.execute(text("""
            UPDATE tenants 
            SET preferred_contact_method = 'email'::contact_method,
                status = CASE 
                    WHEN is_active THEN 'active'::tenant_status 
                    ELSE 'inactive'::tenant_status 
                END
        """))
        
        # Hacer NOT NULL las columnas requeridas
        connection.execute(text("""
            ALTER TABLE tenants
            ALTER COLUMN preferred_contact_method SET NOT NULL,
            ALTER COLUMN status SET NOT NULL,
            ALTER COLUMN preferred_contact_method SET DEFAULT 'email'::contact_method,
            ALTER COLUMN status SET DEFAULT 'pending'::tenant_status
        """))
            
    except Exception as e:
        print(f"Error updating tenants table: {e}")
        raise
        
    # 2. Actualizar tabla contracts
    try:
        # Crear nuevos tipos enum
        with connection.begin_nested():
            connection.execute(text("DROP TYPE IF EXISTS contract_status CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS payment_frequency CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS payment_method CASCADE"))
            
            connection.execute(text("""
                CREATE TYPE contract_status AS ENUM ('draft', 'active', 'expired', 'terminated', 'renewed')
            """))
            connection.execute(text("""
                CREATE TYPE payment_frequency AS ENUM ('monthly', 'bimonthly', 'quarterly', 'semiannual', 'annual')
            """))
            connection.execute(text("""
                CREATE TYPE payment_method AS ENUM ('cash', 'transfer', 'check')
            """))
            
        # Convertir columna status a varchar temporalmente
        with connection.begin_nested():
            connection.execute(text("""
                ALTER TABLE contracts 
                ALTER COLUMN status TYPE varchar(50)
            """))
            
            # Actualizar valores de status
            connection.execute(text("""
                UPDATE contracts 
                SET status = LOWER(status)
            """))
            
            # Convertir a nuevo enum
            connection.execute(text("""
                ALTER TABLE contracts 
                ALTER COLUMN status TYPE contract_status 
                USING status::contract_status
            """))
            
        # Agregar nuevas columnas
        connection.execute(text("""
            ALTER TABLE contracts
            ADD COLUMN IF NOT EXISTS contract_number VARCHAR UNIQUE,
            ADD COLUMN IF NOT EXISTS payment_frequency payment_frequency,
            ADD COLUMN IF NOT EXISTS payment_method payment_method,
            ADD COLUMN IF NOT EXISTS utilities_included JSONB,
            ADD COLUMN IF NOT EXISTS guarantor_info JSONB,
            ADD COLUMN IF NOT EXISTS terms_and_conditions VARCHAR,
            ADD COLUMN IF NOT EXISTS special_conditions VARCHAR
        """))
        
        # Convertir y renombrar monthly_rent a rent_amount
        connection.execute(text("""
            ALTER TABLE contracts
            ALTER COLUMN monthly_rent TYPE FLOAT USING monthly_rent::float
        """))
        
        # Establecer valores por defecto
        connection.execute(text("""
            UPDATE contracts 
            SET payment_frequency = 'monthly'::payment_frequency,
                payment_method = 'transfer'::payment_method,
                utilities_included = '[]'::jsonb,
                terms_and_conditions = 'Términos y condiciones estándar'
            WHERE payment_frequency IS NULL
        """))
        
        # Hacer NOT NULL las columnas requeridas
        connection.execute(text("""
            ALTER TABLE contracts
            ALTER COLUMN payment_frequency SET NOT NULL,
            ALTER COLUMN payment_method SET NOT NULL,
            ALTER COLUMN utilities_included SET NOT NULL,
            ALTER COLUMN terms_and_conditions SET NOT NULL,
            ALTER COLUMN payment_frequency SET DEFAULT 'monthly'::payment_frequency,
            ALTER COLUMN payment_method SET DEFAULT 'transfer'::payment_method,
            ALTER COLUMN utilities_included SET DEFAULT '[]'::jsonb
        """))
            
    except Exception as e:
        print(f"Error updating contracts table: {e}")
        raise
        
    # 3. Crear tabla contract_documents
    try:
        with connection.begin_nested():
            connection.execute(text("""
                CREATE TABLE IF NOT EXISTS contract_documents (
                    id SERIAL PRIMARY KEY,
                    contract_id INTEGER REFERENCES contracts(id),
                    document_type VARCHAR NOT NULL,
                    file_path VARCHAR NOT NULL,
                    upload_date DATE NOT NULL,
                    is_signed BOOLEAN DEFAULT FALSE,
                    signed_date DATE,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
                    updated_at TIMESTAMP WITH TIME ZONE,
                    created_by INTEGER,
                    updated_by INTEGER
                )
            """))
            
    except Exception as e:
        print(f"Error creating contract_documents table: {e}")
        raise

def downgrade():
    connection = op.get_bind()
    
    # 1. Revertir cambios en tenants
    try:
        with connection.begin_nested():
            # Eliminar columnas nuevas
            connection.execute(text("""
                ALTER TABLE tenants
                DROP COLUMN IF EXISTS occupation,
                DROP COLUMN IF EXISTS monthly_income,
                DROP COLUMN IF EXISTS previous_address,
                DROP COLUMN IF EXISTS preferred_contact_method,
                DROP COLUMN IF EXISTS notes,
                DROP COLUMN IF EXISTS date_of_birth,
                DROP COLUMN IF EXISTS employer,
                DROP COLUMN IF EXISTS status
            """))
            
            # Eliminar tipos enum
            connection.execute(text("DROP TYPE IF EXISTS contact_method CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS tenant_status CASCADE"))
            
    except Exception as e:
        print(f"Error reverting tenants table: {e}")
        raise
        
    # 2. Revertir cambios en contracts
    try:
        with connection.begin_nested():
            # Eliminar columnas nuevas
            connection.execute(text("""
                ALTER TABLE contracts
                DROP COLUMN IF EXISTS contract_number,
                DROP COLUMN IF EXISTS payment_frequency,
                DROP COLUMN IF EXISTS payment_method,
                DROP COLUMN IF EXISTS utilities_included,
                DROP COLUMN IF EXISTS guarantor_info,
                DROP COLUMN IF EXISTS terms_and_conditions,
                DROP COLUMN IF EXISTS special_conditions
            """))
            
            # Convertir status de vuelta a mayúsculas
            connection.execute(text("""
                ALTER TABLE contracts 
                ALTER COLUMN status TYPE varchar(50)
            """))
            
            connection.execute(text("""
                UPDATE contracts 
                SET status = UPPER(status)
            """))
            
            # Eliminar tipos enum
            connection.execute(text("DROP TYPE IF EXISTS contract_status CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS payment_frequency CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS payment_method CASCADE"))
            
    except Exception as e:
        print(f"Error reverting contracts table: {e}")
        raise
        
    # 3. Eliminar tabla contract_documents
    try:
        with connection.begin_nested():
            connection.execute(text("DROP TABLE IF EXISTS contract_documents"))
            
    except Exception as e:
        print(f"Error dropping contract_documents table: {e}")
        raise
