# API de Reportes de Gastos

## Descripción General
API para generar y exportar reportes detallados de gastos.

## Base URL
```
/api/v1/expense-reports
```

## Endpoints

### 1. Resumen de Gastos
```http
GET /api/v1/expense-reports/summary
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
    "total_amount": 15000.75,
    "total_count": 45,
    "average_amount": 333.35
  }
}
```

### 2. Tendencias de Gastos
```http
GET /api/v1/expense-reports/trends
```

#### Parámetros de Query
- `start_date`: Fecha inicial (YYYY-MM-DD)
- `end_date`: Fecha final (YYYY-MM-DD)
- `group_by`: Agrupación (day, week, month, year)

#### Respuesta Exitosa (200 OK)
```json
{
  "trends": [
    {
      "period": "2024-01",
      "total_amount": 5000.25,
      "count": 15
    },
    {
      "period": "2024-02",
      "total_amount": 4800.50,
      "count": 12
    }
  ]
}
```

### 3. Distribución por Categoría
```http
GET /api/v1/expense-reports/category-distribution
```

#### Parámetros de Query
- `start_date`: Fecha inicial (YYYY-MM-DD)
- `end_date`: Fecha final (YYYY-MM-DD)

#### Respuesta Exitosa (200 OK)
```json
{
  "distribution": [
    {
      "category": "Mantenimiento",
      "total_amount": 8000.50,
      "count": 25,
      "percentage": 53.33
    },
    {
      "category": "Servicios",
      "total_amount": 7000.25,
      "count": 20,
      "percentage": 46.67
    }
  ]
}
```

### 4. Comparación de Propiedades
```http
GET /api/v1/expense-reports/property-comparison
```

#### Parámetros de Query
- `start_date`: Fecha inicial (YYYY-MM-DD)
- `end_date`: Fecha final (YYYY-MM-DD)

#### Respuesta Exitosa (200 OK)
```json
{
  "comparison": [
    {
      "property": "Propiedad A",
      "total_amount": 8500.75,
      "count": 28,
      "average_amount": 303.60
    },
    {
      "property": "Propiedad B",
      "total_amount": 6500.00,
      "count": 17,
      "average_amount": 382.35
    }
  ]
}
```

### 5. Exportar Reporte
```http
GET /api/v1/expense-reports/export
```

#### Parámetros de Query
- `start_date`: Fecha inicial (YYYY-MM-DD)
- `end_date`: Fecha final (YYYY-MM-DD)
- `format`: Formato de exportación (excel, csv)
- `report_type`: Tipo de reporte (summary, detailed, category, property)

#### Respuesta Exitosa (200 OK)
```json
{
  "filename": "expense_report_20240120.xlsx",
  "file_url": "/uploads/reports/expense_report_20240120.xlsx",
  "generated_at": "2024-01-20T15:30:00Z"
}
```

## Permisos Requeridos

- `expense_report.view`: Ver reportes básicos
- `expense_report.export`: Exportar reportes
- `expense_report.detailed`: Ver reportes detallados

## Formatos de Exportación

1. **Excel**
   - Formato: XLSX
   - Múltiples hojas por reporte
   - Gráficos incluidos

2. **CSV**
   - Formato: CSV
   - Un archivo por tipo de reporte
   - Codificación UTF-8

## Límites y Restricciones

1. **Rangos de Fecha**
   - Máximo 1 año por consulta
   - Fechas no pueden ser futuras

2. **Exportación**
   - Máximo 10,000 registros por exportación
   - Tamaño máximo de archivo: 50MB

3. **Cache**
   - Los reportes se cachean por 1 hora
   - Los reportes exportados se eliminan después de 7 días
