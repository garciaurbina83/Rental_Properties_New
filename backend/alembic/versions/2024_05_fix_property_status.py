"""fix property status enum and constraints

Revision ID: 2024_05_fix_property
Revises: 2024_04_sync_models
Create Date: 2024-12-03 00:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision = '2024_05_fix_property'
down_revision = '2024_04_sync_models'
branch_labels = None
depends_on = None

def upgrade():
    connection = op.get_bind()
    
    # 1. Crear nuevo tipo enum con los valores correctos
    try:
        with connection.begin_nested():
            # Primero convertimos la columna a varchar para poder recrear el enum
            connection.execute(text("""
                ALTER TABLE properties 
                ALTER COLUMN status TYPE varchar(50)
            """))
            
            # Eliminamos el enum antiguo
            connection.execute(text("DROP TYPE IF EXISTS propertystatus CASCADE"))
            
            # Creamos el nuevo enum con los valores correctos
            connection.execute(text("""
                CREATE TYPE propertystatus AS ENUM ('available', 'rented', 'maintenance')
            """))
            
            # Convertimos los valores existentes al nuevo formato
            connection.execute(text("""
                UPDATE properties 
                SET status = CASE 
                    WHEN status = 'AVAILABLE' THEN 'available'
                    WHEN status = 'RENTED' THEN 'rented'
                    WHEN status = 'MAINTENANCE' THEN 'maintenance'
                    WHEN status = 'INACTIVE' THEN 'available'
                    ELSE 'available'
                END
            """))
            
            # Convertimos la columna al nuevo tipo enum
            connection.execute(text("""
                ALTER TABLE properties 
                ALTER COLUMN status TYPE propertystatus 
                USING status::propertystatus
            """))
            
            # Establecemos el valor por defecto y not null
            connection.execute(text("""
                ALTER TABLE properties 
                ALTER COLUMN status SET DEFAULT 'available'::propertystatus,
                ALTER COLUMN status SET NOT NULL
            """))
            
    except Exception as e:
        print(f"Error updating property status: {e}")
        raise
        
    # 2. Hacer address not null
    try:
        with connection.begin_nested():
            # Primero establecemos un valor por defecto para las filas que tengan NULL
            connection.execute(text("""
                UPDATE properties 
                SET address = 'Sin dirección'
                WHERE address IS NULL
            """))
            
            # Luego hacemos la columna not null
            connection.execute(text("""
                ALTER TABLE properties 
                ALTER COLUMN address SET NOT NULL
            """))
    except Exception as e:
        print(f"Error making address not null: {e}")
        raise

def downgrade():
    connection = op.get_bind()
    
    # 1. Revertir los cambios del enum
    try:
        with connection.begin_nested():
            # Convertir a varchar
            connection.execute(text("""
                ALTER TABLE properties 
                ALTER COLUMN status TYPE varchar(50)
            """))
            
            # Eliminar el enum
            connection.execute(text("DROP TYPE IF EXISTS propertystatus CASCADE"))
            
            # Crear el enum antiguo
            connection.execute(text("""
                CREATE TYPE propertystatus AS ENUM ('AVAILABLE', 'RENTED', 'MAINTENANCE', 'INACTIVE')
            """))
            
            # Convertir los valores
            connection.execute(text("""
                UPDATE properties 
                SET status = CASE 
                    WHEN status = 'available' THEN 'AVAILABLE'
                    WHEN status = 'rented' THEN 'RENTED'
                    WHEN status = 'maintenance' THEN 'MAINTENANCE'
                    ELSE 'AVAILABLE'
                END
            """))
            
            # Convertir la columna al tipo enum antiguo
            connection.execute(text("""
                ALTER TABLE properties 
                ALTER COLUMN status TYPE propertystatus 
                USING status::propertystatus
            """))
            
            # Quitar not null y default
            connection.execute(text("""
                ALTER TABLE properties 
                ALTER COLUMN status DROP NOT NULL,
                ALTER COLUMN status DROP DEFAULT
            """))
    except Exception as e:
        print(f"Error reverting property status: {e}")
        raise
        
    # 2. Revertir address a nullable
    try:
        with connection.begin_nested():
            connection.execute(text("""
                ALTER TABLE properties 
                ALTER COLUMN address DROP NOT NULL
            """))
    except Exception as e:
        print(f"Error making address nullable: {e}")
        raise
