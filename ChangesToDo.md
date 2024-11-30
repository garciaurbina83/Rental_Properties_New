# Plan de Implementación: Propiedades Principales y Units

## 1. Modificar el Modelo de Property
```python
# Añadir nuevo Enum para tipos de propiedad
class PropertyType(str, enum.Enum):
    PRINCIPAL = "principal"
    UNIT = "unit"

# Modificar la clase Property
property_type = Column(Enum(PropertyType), nullable=False)
parent_property_id = Column(Integer, ForeignKey('properties.id'), nullable=True)
units = relationship("Property", backref=backref("parent", remote_side=[id]))
```

## 2. Actualizar los Schemas
```python
# Modificar PropertyBase
property_type: PropertyType
parent_property_id: Optional[int] = None
units: Optional[List["Property"]] = None

# Nuevo schema para respuesta de Units
class PropertyWithUnits(Property):
    units: List[Property] = []
```

## 3. Modificar los Servicios (property_service.py)
### Nuevas funciones necesarias:
```python
async def create_unit(db, principal_id: int, unit_data: PropertyCreate)
async def get_property_with_units(db, property_id: int)
async def get_units_by_principal(db, principal_id: int)
```
### Validaciones adicionales:
- Verificar que una Unit solo pueda ser creada para una propiedad Principal
- Verificar que una Unit no pueda tener otras Units
- Validar que el parent_property_id exista y sea de tipo Principal

## 4. Actualizar los Endpoints
```python
# Nuevos endpoints en property.py
@router.post("/properties/{principal_id}/units")
async def create_unit(principal_id: int, unit_data: PropertyCreate)

@router.get("/properties/{principal_id}/units")
async def get_property_units(principal_id: int)

@router.get("/properties/{property_id}/with-units")
async def get_property_with_units(property_id: int)
```

## 5. Tests a Implementar
```python
# En test_property.py
async def test_create_principal_property():
    # Verificar creación de propiedad principal

async def test_create_unit():
    # Verificar creación de unit asociada a principal

async def test_create_unit_invalid_parent():
    # Verificar que falle al crear unit con parent inválido

async def test_get_property_with_units():
    # Verificar obtención de propiedad con sus units

async def test_unit_cannot_have_units():
    # Verificar que una unit no puede tener sub-units

async def test_bulk_update_with_units():
    # Verificar actualización masiva respetando jerarquía
```

## 6. Migración de Base de Datos
```python
# Crear nueva migración para:
- Añadir columna property_type
- Añadir columna parent_property_id
- Añadir foreign key constraint
```

## 7. Validaciones Adicionales
- Verificar permisos específicos para gestión de Units
- Validar que al eliminar una propiedad Principal se manejen sus Units
- Implementar reglas de negocio específicas para cada tipo

## 8. Documentación
- Actualizar la documentación de la API
- Documentar nuevos endpoints
- Actualizar ejemplos de uso
- Documentar reglas de negocio para Principal/Units

## Orden Sugerido de Implementación
1. Modelo y Schemas (Base de la implementación)
2. Migración de Base de Datos
3. Servicios y Validaciones
4. Endpoints
5. Tests
6. Documentación