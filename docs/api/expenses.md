# API de Gestión de Gastos

## Descripción General
La API de Gestión de Gastos proporciona endpoints para administrar gastos, incluyendo creación, actualización, aprobación y generación de reportes.

## Base URL
```
/api/v1/expenses
```

## Autenticación
Todos los endpoints requieren autenticación mediante token JWT en el header:
```
Authorization: Bearer {token}
```

## Endpoints

### 1. Crear Gasto
```http
POST /api/v1/expenses/
```

Crea un nuevo gasto en el sistema.

#### Request Body
```json
{
  "amount": 100.50,
  "date": "2024-01-20",
  "description": "Mantenimiento mensual",
  "expense_type": "maintenance",
  "property_id": 1,
  "vendor_id": 1,
  "category_id": 1,
  "is_recurring": false,
  "custom_fields": {
    "invoice_number": "INV-001"
  }
}
```

#### Respuesta Exitosa (200 OK)
```json
{
  "id": 1,
  "amount": 100.50,
  "date": "2024-01-20",
  "description": "Mantenimiento mensual",
  "status": "pending_approval",
  "created_by": {
    "id": 1,
    "email": "user@example.com"
  },
  "created_at": "2024-01-20T10:30:00Z"
}
```

### 2. Obtener Gasto
```http
GET /api/v1/expenses/{expense_id}
```

Obtiene los detalles de un gasto específico.

#### Parámetros de URL
- `expense_id`: ID del gasto (integer)

#### Respuesta Exitosa (200 OK)
```json
{
  "id": 1,
  "amount": 100.50,
  "date": "2024-01-20",
  "description": "Mantenimiento mensual",
  "status": "pending_approval",
  "expense_type": "maintenance",
  "property": {
    "id": 1,
    "name": "Propiedad A"
  },
  "vendor": {
    "id": 1,
    "name": "Proveedor A"
  },
  "category": {
    "id": 1,
    "name": "Mantenimiento"
  },
  "created_by": {
    "id": 1,
    "email": "user@example.com"
  },
  "created_at": "2024-01-20T10:30:00Z",
  "custom_fields": {
    "invoice_number": "INV-001"
  }
}
```

### 3. Actualizar Gasto
```http
PUT /api/v1/expenses/{expense_id}
```

Actualiza un gasto existente.

#### Request Body
```json
{
  "amount": 150.75,
  "description": "Mantenimiento mensual actualizado",
  "category_id": 2
}
```

#### Respuesta Exitosa (200 OK)
```json
{
  "id": 1,
  "amount": 150.75,
  "description": "Mantenimiento mensual actualizado",
  "status": "pending_approval"
}
```

### 4. Aprobar Gasto
```http
POST /api/v1/expenses/{expense_id}/approve
```

Aprueba un gasto pendiente.

#### Respuesta Exitosa (200 OK)
```json
{
  "id": 1,
  "status": "approved",
  "approved_by": {
    "id": 2,
    "email": "approver@example.com"
  },
  "approved_at": "2024-01-21T15:45:00Z"
}
```

### 5. Rechazar Gasto
```http
POST /api/v1/expenses/{expense_id}/reject
```

#### Request Body
```json
{
  "rejection_reason": "Documentación incompleta"
}
```

#### Respuesta Exitosa (200 OK)
```json
{
  "id": 1,
  "status": "rejected",
  "rejection_reason": "Documentación incompleta",
  "rejected_by": {
    "id": 2,
    "email": "approver@example.com"
  },
  "rejected_at": "2024-01-21T15:45:00Z"
}
```

### 6. Obtener Resumen de Gastos
```http
GET /api/v1/expenses/summary
```

#### Parámetros de Query
- `start_date`: Fecha inicial (YYYY-MM-DD)
- `end_date`: Fecha final (YYYY-MM-DD)
- `property_id`: ID de la propiedad (opcional)
- `category_id`: ID de la categoría (opcional)

#### Respuesta Exitosa (200 OK)
```json
{
  "period": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "summary": {
    "total_amount": 1500.25,
    "total_count": 10,
    "average_amount": 150.03
  },
  "by_category": [
    {
      "category": "Mantenimiento",
      "total_amount": 800.50,
      "count": 5
    }
  ],
  "by_status": [
    {
      "status": "approved",
      "total_amount": 1200.00,
      "count": 8
    }
  ]
}
```

### 7. Exportar Gastos
```http
GET /api/v1/expenses/export
```

#### Parámetros de Query
- `start_date`: Fecha inicial (YYYY-MM-DD)
- `end_date`: Fecha final (YYYY-MM-DD)
- `format`: Formato de exportación (excel, csv)

#### Respuesta Exitosa (200 OK)
```json
{
  "filename": "expenses_20240120_153000.xlsx",
  "file_url": "/uploads/reports/expenses_20240120_153000.xlsx"
}
```

## Códigos de Estado

- `200 OK`: Solicitud exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Error en los datos enviados
- `401 Unauthorized`: No autenticado
- `403 Forbidden`: No autorizado
- `404 Not Found`: Recurso no encontrado
- `422 Unprocessable Entity`: Error de validación

## Modelos de Datos

### Expense
```json
{
  "id": "integer",
  "amount": "decimal",
  "date": "date",
  "description": "string",
  "expense_type": "string (maintenance, utilities, taxes, other)",
  "status": "string (pending_approval, approved, rejected)",
  "property_id": "integer",
  "vendor_id": "integer",
  "category_id": "integer",
  "created_by_id": "integer",
  "created_at": "datetime",
  "approved_by": "integer",
  "approved_at": "datetime",
  "rejection_reason": "string",
  "is_recurring": "boolean",
  "recurrence_interval": "string",
  "custom_fields": "object"
}
```

## Permisos Requeridos

- `expense.create`: Crear gastos
- `expense.read`: Ver gastos
- `expense.update`: Actualizar gastos
- `expense.delete`: Eliminar gastos
- `expense.approve`: Aprobar gastos
- `expense.export`: Exportar reportes

## Límites y Restricciones

1. **Límites de Aprobación**
   - Los usuarios tienen límites de aprobación configurados
   - No se puede aprobar gastos que excedan el límite

2. **Validaciones**
   - El monto debe ser positivo
   - La fecha no puede ser futura
   - Los gastos aprobados no se pueden modificar

3. **Archivos Adjuntos**
   - Máximo 5 archivos por gasto
   - Tamaño máximo por archivo: 10MB
   - Formatos permitidos: PDF, JPG, PNG
