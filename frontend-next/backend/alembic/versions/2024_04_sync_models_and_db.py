"""sync models and database tables

Revision ID: 2024_04_sync_models
Revises: 2024_03_merge_heads
Create Date: 2024-12-02 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

# revision identifiers, used by Alembic.
revision = '2024_04_sync_models'
down_revision = '2024_03_merge_heads'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()
    
    # Crear tipos enum
    try:
        # Crear tipos enum en una transacción separada
        with connection.begin_nested():
            connection.execute(text("DROP TYPE IF EXISTS ticket_status CASCADE"))
            connection.execute(text("DROP TYPE IF EXISTS ticket_priority CASCADE"))
            connection.execute(text("CREATE TYPE ticket_status AS ENUM ('OPEN', 'IN_PROGRESS', 'PENDING', 'RESOLVED', 'CLOSED')"))
            connection.execute(text("CREATE TYPE ticket_priority AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'URGENT')"))
    except Exception as e:
        print(f"Error creating enum types: {e}")
        raise
    
    # Asegurar que todas las tablas tengan campos de auditoría
    tables_to_update = [
        'properties', 'units', 'tenants', 'contracts', 'payments',
        'maintenance_tickets', 'maintenance_requests', 'expenses',
        'loans', 'vendors', 'users'
    ]
    
    for table in tables_to_update:
        # Agregar campos de auditoría si no existen
        columns_to_add = {
            'created_at': sa.DateTime(timezone=True),
            'updated_at': sa.DateTime(timezone=True),
            'created_by': sa.Integer(),
            'updated_by': sa.Integer()
        }
        
        for column_name, column_type in columns_to_add.items():
            try:
                # Cada alteración de tabla en su propia transacción anidada
                with connection.begin_nested():
                    op.add_column(table, sa.Column(column_name, column_type))
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"Error adding column {column_name} to table {table}: {e}")
                    raise
    
    # Actualizar tipos de datos y restricciones
    try:
        # Verificar si la tabla existe antes de intentar actualizarla
        with connection.begin_nested():
            result = connection.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'maintenance_tickets'
                )
            """)).scalar()
            
            if result:
                # Agregar la columna status si no existe
                try:
                    with connection.begin_nested():
                        connection.execute(text("""
                            ALTER TABLE maintenance_tickets 
                            ADD COLUMN IF NOT EXISTS status VARCHAR(50)
                        """))
                except Exception as e:
                    print(f"Error adding status column: {e}")

                # Convertir las columnas a los nuevos tipos primero
                with connection.begin_nested():
                    connection.execute(text("""
                        ALTER TABLE maintenance_tickets 
                        ALTER COLUMN status TYPE ticket_status 
                        USING CASE 
                            WHEN status = 'OPEN' THEN 'OPEN'::ticket_status
                            WHEN status = 'IN_PROGRESS' THEN 'IN_PROGRESS'::ticket_status
                            WHEN status = 'PENDING' THEN 'PENDING'::ticket_status
                            WHEN status = 'RESOLVED' THEN 'RESOLVED'::ticket_status
                            WHEN status = 'CLOSED' THEN 'CLOSED'::ticket_status
                            ELSE 'OPEN'::ticket_status
                        END
                    """))
                
                with connection.begin_nested():
                    connection.execute(text("""
                        ALTER TABLE maintenance_tickets 
                        ALTER COLUMN priority TYPE ticket_priority 
                        USING CASE 
                            WHEN priority = 'LOW' THEN 'LOW'::ticket_priority
                            WHEN priority = 'MEDIUM' THEN 'MEDIUM'::ticket_priority
                            WHEN priority = 'HIGH' THEN 'HIGH'::ticket_priority
                            WHEN priority = 'URGENT' THEN 'URGENT'::ticket_priority
                            ELSE 'LOW'::ticket_priority
                        END
                    """))
                
                # Luego actualizar los valores nulos o inválidos
                with connection.begin_nested():
                    connection.execute(text("""
                        UPDATE maintenance_tickets 
                        SET status = 'OPEN'::ticket_status 
                        WHERE status IS NULL
                    """))
                
                with connection.begin_nested():
                    connection.execute(text("""
                        UPDATE maintenance_tickets 
                        SET priority = 'LOW'::ticket_priority 
                        WHERE priority IS NULL
                    """))
                
                # Agregar restricciones NOT NULL después de asegurarnos que todos los valores son válidos
                with connection.begin_nested():
                    connection.execute(text("""
                        ALTER TABLE maintenance_tickets 
                        ALTER COLUMN status SET NOT NULL,
                        ALTER COLUMN priority SET NOT NULL
                    """))
                
                # Crear índices para mejorar el rendimiento de las búsquedas
                with connection.begin_nested():
                    connection.execute(text("""
                        CREATE INDEX IF NOT EXISTS idx_maintenance_tickets_status ON maintenance_tickets (status);
                        CREATE INDEX IF NOT EXISTS idx_maintenance_tickets_priority ON maintenance_tickets (priority);
                    """))
    except Exception as e:
        print(f"Error updating maintenance_tickets table: {e}")
        raise

def downgrade():
    connection = op.get_bind()
    
    try:
        # Eliminar índices
        op.drop_index(op.f('ix_properties_created_at'), 'properties')
        op.drop_index(op.f('ix_maintenance_tickets_status'), 'maintenance_tickets')
        op.drop_index(op.f('ix_payments_due_date'), 'payments')
        op.drop_index(op.f('ix_contracts_start_date'), 'contracts')
        op.drop_index(op.f('ix_contracts_end_date'), 'contracts')
        
        # Revertir tipos de datos
        connection.execute(text("""
            ALTER TABLE maintenance_tickets 
            ALTER COLUMN status TYPE varchar(50)
            USING status::varchar
        """))
        
        connection.execute(text("""
            ALTER TABLE maintenance_tickets 
            ALTER COLUMN priority TYPE varchar(50)
            USING priority::varchar
        """))
        
        # Eliminar tipos enum
        connection.execute(text("DROP TYPE IF EXISTS ticket_status CASCADE"))
        connection.execute(text("DROP TYPE IF EXISTS ticket_priority CASCADE"))
    except ProgrammingError:
        connection.rollback()
        raise
