# Sistema de Pagos

## Descripción General
El sistema de pagos es un módulo central que gestiona todas las transacciones financieras relacionadas con las propiedades en alquiler. Proporciona funcionalidades para el registro, seguimiento y gestión de pagos, incluyendo validaciones, notificaciones y reportes.

## Características Principales

### 1. Gestión de Pagos
- Registro de pagos de alquiler y otros conceptos
- Actualización y seguimiento del estado de pagos
- Validación de montos y fechas
- Asociación con contratos y inquilinos

### 2. Estados de Pago
- `PENDING`: Pago pendiente
- `PAID`: Pago completado
- `OVERDUE`: Pago vencido
- `CANCELLED`: Pago cancelado
- `REFUNDED`: Pago reembolsado

### 3. Conceptos de Pago
- `RENT`: Pago de alquiler
- `DEPOSIT`: Depósito de garantía
- `MAINTENANCE`: Gastos de mantenimiento
- `UTILITIES`: Servicios públicos
- `OTHER`: Otros conceptos

### 4. Validaciones
- Monto positivo
- Fecha válida
- Contrato activo
- Inquilino válido
- No duplicación de pagos
- Estado del contrato

### 5. Notificaciones
- Recordatorios de pagos próximos
- Confirmaciones de pago
- Alertas de pagos vencidos
- Notificaciones de cambio de estado

### 6. Reportes
- Estado de cuenta
- Historial de pagos
- Pagos vencidos
- Análisis de pagos

## API Endpoints

### Pagos
```
GET /api/v1/payments/
POST /api/v1/payments/
GET /api/v1/payments/{id}
PUT /api/v1/payments/{id}
DELETE /api/v1/payments/{id}
```

### Reportes
```
GET /api/v1/payments/contract/{contract_id}/summary
GET /api/v1/payments/tenant/{tenant_id}/history
GET /api/v1/reports/payments/overdue
GET /api/v1/reports/payments/analytics
```

## Modelos de Datos

### Payment
```python
class Payment(BaseModel):
    id: int
    amount: float
    payment_date: date
    concept: PaymentConcept
    status: PaymentStatus
    contract_id: int
    tenant_id: int
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    processed_by_id: Optional[int]
```

## Integraciones

### 1. Contratos
- Validación de estado del contrato
- Cálculo de montos pendientes
- Historial de pagos por contrato

### 2. Inquilinos
- Historial de pagos por inquilino
- Estado de cuenta
- Métricas de puntualidad

### 3. Propiedades
- Ingresos por propiedad
- Métricas financieras
- Análisis de rentabilidad

## Seguridad y Auditoría

### 1. Control de Acceso
- Solo usuarios autorizados pueden crear/modificar pagos
- Registro de usuario que procesa el pago
- Validación de permisos por rol

### 2. Auditoría
- Registro de todas las operaciones
- Historial de cambios
- Trazabilidad completa
- Registro de IP y user-agent

## Ejemplos de Uso

### 1. Crear un Pago
```python
payment_data = {
    "amount": 1000.0,
    "payment_date": "2024-01-15",
    "concept": "RENT",
    "status": "PENDING",
    "contract_id": 1,
    "tenant_id": 1,
    "description": "Alquiler enero 2024"
}
response = client.post("/api/v1/payments/", json=payment_data)
```

### 2. Obtener Historial de Pagos
```python
# Por contrato
payments = client.get("/api/v1/payments/contract/1/summary")

# Por inquilino
payments = client.get("/api/v1/payments/tenant/1/history")
```

### 3. Generar Reporte
```python
# Reporte de pagos vencidos
report = client.get("/api/v1/reports/payments/overdue")

# Análisis de pagos
analytics = client.get("/api/v1/reports/payments/analytics")
```

## Mejores Prácticas

1. **Validación de Datos**
   - Validar montos y fechas
   - Verificar estado del contrato
   - Evitar duplicación de pagos

2. **Gestión de Estados**
   - Mantener consistencia en estados
   - Validar transiciones válidas
   - Registrar cambios de estado

3. **Notificaciones**
   - Enviar confirmaciones inmediatas
   - Programar recordatorios
   - Mantener plantillas actualizadas

4. **Seguridad**
   - Validar permisos
   - Registrar auditoría
   - Proteger datos sensibles

## Mantenimiento y Soporte

1. **Monitoreo**
   - Registro de errores
   - Métricas de rendimiento
   - Alertas automáticas

2. **Respaldos**
   - Backup diario de transacciones
   - Registro de auditoría
   - Historial de cambios

3. **Actualizaciones**
   - Registro de versiones
   - Documentación de cambios
   - Plan de rollback
