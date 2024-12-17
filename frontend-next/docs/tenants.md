# Inquilinos

## Endpoints

### Crear Inquilino
```http
POST /api/v1/tenants
```

Crear un nuevo inquilino en el sistema.

**Request Body:**
```json
{
  "first_name": "Juan",
  "last_name": "Pérez",
  "email": "juan.perez@email.com",
  "phone": "555-0123",
  "identification_type": "INE",
  "identification_number": "IDMX123456",
  "date_of_birth": "1990-05-15",
  "occupation": "Ingeniero",
  "monthly_income": 5000.00,
  "preferred_contact_method": "EMAIL",
  "emergency_contact": {
    "name": "María Pérez",
    "relationship": "Madre",
    "phone": "555-4567",
    "email": "maria.perez@email.com"
  },
  "references": [
    {
      "name": "Pedro González",
      "relationship": "Anterior Arrendador",
      "phone": "555-7890",
      "email": "pedro@email.com",
      "reference_type": "LANDLORD"
    },
    {
      "name": "Ana Martínez",
      "relationship": "Empleador",
      "phone": "555-0987",
      "email": "ana@empresa.com",
      "reference_type": "EMPLOYER"
    }
  ]
}
```

**Response:** `201 Created`

### Documentos del Inquilino
```http
POST /api/v1/tenants/{tenant_id}/documents
```

Agregar un nuevo documento al inquilino.

**Request Body:**
```json
{
  "document_type": "IDENTIFICATION",
  "file_path": "/documents/ine-tenant-1.pdf",
  "description": "INE del inquilino",
  "expiration_date": "2030-12-31"
}
```

### Validaciones

1. **Información Personal:**
   - Email debe ser válido
   - Teléfono debe tener un formato válido
   - Fecha de nacimiento debe indicar que es mayor de edad

2. **Referencias:**
   - Se requiere al menos una referencia
   - Debe incluir información de contacto completa
   - Se recomienda una referencia de arrendador anterior y una laboral

3. **Documentos:**
   - Identificación oficial vigente
   - Comprobante de ingresos reciente
   - Comprobante de domicilio

4. **Información Financiera:**
   - El ingreso mensual debe ser reportado
   - Se recomienda que el ingreso mensual sea al menos 3 veces el monto de la renta

## Reglas de Negocio

### Evaluación de Inquilinos

1. **Criterios de Aprobación:**
   - Verificación de referencias satisfactoria
   - Ingreso suficiente para cubrir la renta
   - Sin antecedentes de incumplimiento
   - Documentación completa y válida

2. **Proceso de Verificación:**
   - Contacto con referencias proporcionadas
   - Verificación de empleo actual
   - Revisión de historial crediticio (si aplica)
   - Validación de documentos presentados

3. **Motivos de Rechazo:**
   - Referencias negativas
   - Ingreso insuficiente
   - Documentación incompleta o inválida
   - Historial de incumplimiento previo

### Gestión de Documentos

1. **Documentos Requeridos:**
   - Identificación oficial vigente
   - Comprobante de ingresos (últimos 3 meses)
   - Comprobante de domicilio (no mayor a 3 meses)
   - Referencias por escrito
   - Contrato laboral o documentación de empleo

2. **Actualización de Documentos:**
   - Renovación de identificaciones vencidas
   - Actualización periódica de comprobantes de ingresos
   - Mantenimiento de información de contacto actualizada

3. **Almacenamiento:**
   - Documentos almacenados de forma segura
   - Acceso restringido a personal autorizado
   - Respaldo digital de todos los documentos
   - Cumplimiento con leyes de protección de datos
