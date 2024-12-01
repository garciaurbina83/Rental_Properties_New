# Contratos

## Endpoints

### Crear Contrato
```http
POST /api/v1/contracts
```

Crear un nuevo contrato de arrendamiento.

**Request Body:**
```json
{
  "tenant_id": 1,
  "unit_id": 2,
  "contract_number": "CONT-2024-001",
  "start_date": "2024-02-01",
  "end_date": "2025-01-31",
  "rent_amount": 1500.00,
  "security_deposit": 1500.00,
  "payment_frequency": "MONTHLY",
  "payment_due_day": 5,
  "payment_method": "TRANSFER",
  "terms_and_conditions": "Términos y condiciones estándar...",
  "special_conditions": "Condiciones especiales si aplican...",
  "is_renewable": true,
  "renewal_price_increase": 5.0,
  "auto_renewal": false,
  "utilities_included": {
    "water": true,
    "electricity": false,
    "gas": false,
    "internet": false
  },
  "guarantor_info": {
    "name": "Juan Pérez",
    "contact": "555-0123",
    "address": "Calle 123, Ciudad",
    "relationship": "Familiar"
  },
  "documents": [
    {
      "document_type": "identification",
      "file_path": "/documents/id-tenant-1.pdf",
      "upload_date": "2024-01-20",
      "is_signed": true,
      "signed_date": "2024-01-20"
    },
    {
      "document_type": "proof_of_income",
      "file_path": "/documents/income-tenant-1.pdf",
      "upload_date": "2024-01-20",
      "is_signed": false
    },
    {
      "document_type": "contract_agreement",
      "file_path": "/documents/contract-2024-001.pdf",
      "upload_date": "2024-01-20",
      "is_signed": true,
      "signed_date": "2024-01-20"
    }
  ]
}
```

**Response:** `201 Created`

### Validaciones

Al crear o actualizar un contrato, se aplican las siguientes validaciones:

1. **Disponibilidad de la Propiedad:**
   - Verifica que no existan contratos activos o renovados que se superpongan con las fechas solicitadas
   - Considera tanto contratos activos como renovados

2. **Fechas del Contrato:**
   - La fecha de inicio debe ser posterior a la fecha actual
   - La fecha de finalización debe ser posterior a la fecha de inicio

3. **Montos:**
   - El monto de la renta debe ser mayor a 0
   - El depósito de garantía debe ser mayor o igual a 0

4. **Documentos Requeridos:**
   - Se requiere al menos un documento
   - Documentos obligatorios:
     - Identificación (`identification`)
     - Comprobante de ingresos (`proof_of_income`)
     - Contrato firmado (`contract_agreement`)

5. **Información del Garante:**
   Cuando se proporciona información del garante, se requieren los siguientes campos:
   - Nombre (`name`)
   - Contacto (`contact`)
   - Dirección (`address`)
   - Relación con el inquilino (`relationship`)

### Renovar Contrato
```http
POST /api/v1/contracts/{contract_id}/renew
```

Renovar un contrato existente.

**Request Body:**
```json
{
  "new_end_date": "2026-01-31",
  "new_rent_amount": 1575.00
}
```

**Notas:**
- Solo se pueden renovar contratos activos
- Si no se especifica nuevo monto de renta, se calcula automáticamente según el porcentaje de incremento definido en el contrato
- El contrato debe tener la opción `is_renewable` habilitada

### Terminar Contrato
```http
POST /api/v1/contracts/{contract_id}/terminate
```

Terminar un contrato antes de su fecha de finalización.

**Request Body:**
```json
{
  "termination_date": "2024-06-30",
  "termination_notes": "Terminación anticipada por acuerdo mutuo"
}
```

### Procesar Devolución de Depósito
```http
POST /api/v1/contracts/{contract_id}/deposit-refund
```

Procesar la devolución del depósito de garantía.

**Request Body:**
```json
{
  "deductions": 200.00,
  "deduction_reason": "Reparación de daños en paredes"
}
```

**Notas:**
- Solo se puede procesar para contratos terminados o expirados
- Las deducciones no pueden ser negativas
- Las deducciones no pueden exceder el monto del depósito

### Registrar Pago
```http
POST /api/v1/contracts/{contract_id}/payments
```

Registrar un nuevo pago de renta.

**Request Body:**
```json
{
  "amount": 1500.00,
  "payment_date": "2024-02-05",
  "due_date": "2024-02-05",
  "payment_method": "TRANSFER",
  "transaction_id": "TRANS-123456",
  "notes": "Pago mensual febrero 2024"
}
```

**Notas:**
- Solo se pueden registrar pagos para contratos activos o renovados
- Se marca automáticamente como pago tardío si la fecha de pago es posterior a la fecha de vencimiento
