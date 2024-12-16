# API de Categorías de Gastos

## Descripción General
API para gestionar las categorías de gastos, permitiendo una organización jerárquica de los gastos.

## Base URL
```
/api/v1/expense-categories
```

## Endpoints

### 1. Crear Categoría
```http
POST /api/v1/expense-categories/
```

#### Request Body
```json
{
  "name": "Mantenimiento",
  "description": "Gastos de mantenimiento general",
  "parent_id": null,
  "is_active": true
}
```

#### Respuesta Exitosa (200 OK)
```json
{
  "id": 1,
  "name": "Mantenimiento",
  "description": "Gastos de mantenimiento general",
  "parent_id": null,
  "is_active": true,
  "children": []
}
```

### 2. Obtener Categoría
```http
GET /api/v1/expense-categories/{category_id}
```

#### Respuesta Exitosa (200 OK)
```json
{
  "id": 1,
  "name": "Mantenimiento",
  "description": "Gastos de mantenimiento general",
  "parent_id": null,
  "is_active": true,
  "children": [
    {
      "id": 2,
      "name": "Mantenimiento Preventivo",
      "description": "Mantenimiento programado",
      "is_active": true
    }
  ]
}
```

### 3. Listar Categorías
```http
GET /api/v1/expense-categories/
```

#### Parámetros de Query
- `active_only`: Mostrar solo categorías activas (boolean)
- `root_only`: Mostrar solo categorías raíz (boolean)

#### Respuesta Exitosa (200 OK)
```json
{
  "items": [
    {
      "id": 1,
      "name": "Mantenimiento",
      "description": "Gastos de mantenimiento general",
      "children": [
        {
          "id": 2,
          "name": "Mantenimiento Preventivo"
        }
      ]
    }
  ],
  "total": 1
}
```

### 4. Actualizar Categoría
```http
PUT /api/v1/expense-categories/{category_id}
```

#### Request Body
```json
{
  "name": "Mantenimiento General",
  "description": "Gastos de mantenimiento actualizado",
  "is_active": true
}
```

#### Respuesta Exitosa (200 OK)
```json
{
  "id": 1,
  "name": "Mantenimiento General",
  "description": "Gastos de mantenimiento actualizado",
  "is_active": true
}
```

### 5. Eliminar Categoría
```http
DELETE /api/v1/expense-categories/{category_id}
```

#### Respuesta Exitosa (200 OK)
```json
{
  "message": "Category deleted successfully"
}
```

### 6. Obtener Subcategorías
```http
GET /api/v1/expense-categories/{category_id}/children
```

#### Respuesta Exitosa (200 OK)
```json
{
  "items": [
    {
      "id": 2,
      "name": "Mantenimiento Preventivo",
      "description": "Mantenimiento programado",
      "is_active": true
    }
  ],
  "total": 1
}
```

## Modelos de Datos

### ExpenseCategory
```json
{
  "id": "integer",
  "name": "string",
  "description": "string",
  "parent_id": "integer",
  "is_active": "boolean",
  "children": "array[ExpenseCategory]"
}
```

## Permisos Requeridos

- `expense_category.create`: Crear categorías
- `expense_category.read`: Ver categorías
- `expense_category.update`: Actualizar categorías
- `expense_category.delete`: Eliminar categorías

## Restricciones

1. **Jerarquía**
   - Una categoría puede tener múltiples subcategorías
   - Una categoría solo puede tener un padre
   - No se permiten ciclos en la jerarquía

2. **Eliminación**
   - No se puede eliminar una categoría con gastos asociados
   - Al eliminar una categoría padre, se deben reasignar las subcategorías

3. **Nombres**
   - Los nombres de categorías deben ser únicos en el mismo nivel
   - Longitud máxima del nombre: 100 caracteres
