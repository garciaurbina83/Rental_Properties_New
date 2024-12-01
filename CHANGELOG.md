# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Nuevo componente de mapa interactivo para visualizar ubicaciones de propiedades
- Integración con Google Maps API para mostrar propiedades en el mapa
- Marcadores personalizados en el mapa con estados de propiedades
- Panel de rendimiento de propiedades con métricas clave
- Calendario de eventos para seguimiento de actividades
- Lista de tareas con prioridades y fechas de vencimiento
- Sección de alertas para notificaciones importantes
- Panel de acciones rápidas para tareas comunes
- Sistema de autenticación con Clerk
- Dashboard principal con gráficos de Recharts
- Sistema de monitoreo con Prometheus y Grafana
- Configuración de Docker para todos los servicios
- Testing infrastructure setup
  - Created `/tests` directory structure
  - Added integration and E2E test examples
  - Configured pytest with custom markers
  - Added Selenium setup for E2E testing
  - Added unit tests for Settings module
- Requirements organization
  - Moved to a hierarchical requirements structure
  - Added development dependencies in `requirements-dev.txt`
  - Centralized project dependencies in root `requirements.txt`
- Added property type functionality with PRINCIPAL and INVESTMENT options
- Added parent-child relationship between properties
- Added new database migration for property type and parent ID
- Added comprehensive test suite for property API
  - Unit tests for property model and service
  - Integration tests for property endpoints
  - Test fixtures for different property types
- Added comprehensive unit tests for Property API
  - Test cases for property creation validation
  - Test cases for parent-child property relationships
  - Test cases for error handling in property creation
- Validaciones avanzadas para contratos:
  - Verificación de disponibilidad de propiedades
  - Validación de fechas de contrato
  - Validación de montos y depósitos
  - Verificación de documentos requeridos
  - Validación de información del garante
- Documentación completa del sistema:
  - Documentación detallada de la API de contratos
  - Documentación de la API de inquilinos
  - Guía completa de reglas de negocio
  - Ejemplos de uso para todos los endpoints
  - Documentación del proceso de renovación y terminación
  - Guía de gestión de depósitos
- Sistema de mantenimiento básico
  - Gestión de tickets de mantenimiento
  - Seguimiento de estado y prioridad
  - Notificaciones automáticas
  - Registro de costos y resoluciones
  - Filtros y búsqueda avanzada
- Nuevos endpoints para mantenimiento
  - POST /maintenance/tickets/
  - GET /maintenance/tickets/
  - GET /maintenance/tickets/{ticket_id}
  - PUT /maintenance/tickets/{ticket_id}
  - DELETE /maintenance/tickets/{ticket_id}
  - POST /maintenance/tickets/{ticket_id}/close
- Servicio MaintenanceService para lógica de negocio
  - Gestión de tickets vencidos
  - Seguimiento de mantenimientos próximos
  - Integración con sistema de notificaciones

### Changed
- Rediseño completo del dashboard para mejor organización
- Mejora en la visualización de transacciones recientes
- Actualización del sidebar con nuevas secciones
- Optimización del layout para mejor usabilidad
- Mejora en la presentación de estadísticas y KPIs
- Simplificación de la clase Settings
  - Migración de Pydantic a dataclasses para una validación más simple
  - Manejo consistente de variables de entorno en `__post_init__`
  - Mejora en la organización del código de configuración
- Refactored property API to support filtering by user_id
- Improved property test organization and structure
- Enhanced property service with better error handling
- Updated property schema to include new type and parent fields
- Mejorado el sistema de validación de contratos:
  - Implementación de validaciones más robustas y detalladas
  - Mejor manejo de errores con mensajes descriptivos
  - Validaciones asíncronas para verificación de disponibilidad
- Reorganizada y expandida la documentación:
  - Nueva estructura de documentación por módulos
  - Ejemplos de código actualizados y mejorados
  - Documentación más detallada de reglas de negocio
  - Mejor organización de la documentación de la API
- Actualizado api_router para incluir endpoints de mantenimiento
- Mejorada integración con sistema de notificaciones
- Database
  - Resolved Alembic migration conflicts and duplications
  - Restructured migration chain for better organization:
    - Created new migration for users table
    - Fixed vendors table creation to avoid duplication
    - Removed duplicate enum types in loan system
    - Merged migration heads for linear history
  - Enhanced loan system schema:
    - Added payment tracking fields
    - Created loan_documents and loan_payments tables
    - Established proper enum types for loan management

### Backend
- API RESTful con FastAPI
- Integración con PostgreSQL y Redis
- Sistema de migraciones con Alembic
- Tests unitarios y de integración

### Frontend
- Interfaz de usuario con Material-UI
- Gestión de estado con Zustand
- Manejo de datos asíncronos con React Query
- Componentes reutilizables

### DevOps
- Pipeline CI/CD con GitHub Actions
- Configuración de Docker multi-stage
- Nginx como proxy reverso
- Monitoreo con Prometheus y Grafana

### Fixed
- Corrección de estilos en componentes de UI
- Mejora en la responsividad del dashboard
- Optimización de rendimiento en la carga de componentes
- Fixed routing conflict in property API by moving bulk update endpoint before property ID routes
- Corrected bulk update endpoint URL in property API tests
- Fixed property status validation in tests by using lowercase enum values to match PropertyStatus definition
- Updated test fixtures and bulk update test to use correct status values
- Fixed property API tests by using correct fixtures and test data
- Fixed database cleanup in tests to prevent test interference
- Corrected property status validation in tests
- Fixed NameError in cleanup_db fixture by adding missing imports
- Fixed async/await handling in Property API tests
- Fixed error handling in property creation for invalid parent properties
- Fixed Settings module to properly handle environment variables

## [1.1.0] - 2024-01-15

### Added
- Sistema completo de pagos
  - Modelo de pagos con estados y conceptos
  - Endpoints CRUD para gestión de pagos
  - Validaciones de negocio y datos
  - Sistema de notificaciones para pagos
  - Reportes y análisis de pagos
  - Integraciones con contratos y inquilinos
- Sistema de auditoría
  - Registro de todas las operaciones
  - Trazabilidad de cambios
  - Historial completo de modificaciones
- Pruebas unitarias y de integración
  - Cobertura completa del módulo de pagos
  - Pruebas de validaciones y reglas de negocio
  - Pruebas de integración con otros módulos

### Changed
- Mejoras en la estructura de pruebas
  - Reorganización de tests por tipo
  - Separación de pruebas unitarias y de integración
  - Mejora en utilidades de prueba

### Security
- Implementación de auditoría completa
  - Registro de IP y user-agent
  - Control de acceso por rol
  - Validación de permisos

## [1.0.0] - YYYY-MM-DD

### Added
#### Backend
- Modelos iniciales para propiedades, inquilinos y contratos
- Endpoints CRUD para todas las entidades
- Sistema de autenticación y autorización
- Integración con base de datos PostgreSQL
- Cache con Redis
- Documentación Swagger/OpenAPI

#### Frontend
- Diseño de interfaz de usuario con Material-UI
- Páginas principales:
  - Dashboard
  - Gestión de propiedades
  - Gestión de inquilinos
  - Gestión de contratos
- Sistema de autenticación con Clerk
- Integración con API backend

#### DevOps
- Configuración inicial de Docker
- Pipeline CI/CD básico
- Configuración de Nginx
- Monitoreo básico

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Implementación de HTTPS
- Headers de seguridad en Nginx
- Validación de tokens JWT
- Sanitización de inputs

## [0.3.0] - 2024-01-09

### Added
- Implementación del formulario de Agregar Propiedad con campos completos:
  - Información básica (nombre, precio, tipo, estado)
  - Características (habitaciones, baños, metros cuadrados, estacionamientos)
  - Dirección (calle, ciudad, estado, código postal)
  - Descripción
  - Sección para subir imágenes
- Integración de diálogo modal para el formulario de nueva propiedad
- Estado local temporal para manejar nuevas propiedades

### Changed
- Simplificación de la interfaz eliminando el botón redundante "Nueva Propiedad"
- Mejora en la organización del código separando la lógica del formulario en un componente dedicado

## [0.2.0] - 2024-01-08

### Added
- Componentes UI base:
  - Alert para mensajes del sistema
  - Badge para indicadores de estado
  - Dropdown Menu para opciones
  - Input para campos de texto
  - Label para etiquetas de formulario
  - Select para selección de opciones
  - Sheet para paneles deslizantes
  - Table para visualización de datos
  - Tabs para navegación
  - Textarea para texto multilínea
- Tipos TypeScript para:
  - Contratos
  - Pagos
  - Mantenimiento
- Componentes funcionales:
  - PropertyImportExport para importar/exportar datos
  - PropertyReports para generar reportes
  - Paginación para la lista de propiedades

### Changed
- Integración de Radix UI para componentes avanzados
- Mejora en la estructura de archivos del proyecto
- Actualización de dependencias para resolver conflictos

## [0.1.0] - 2024-01-07

### Added
- Configuración inicial del proyecto Next.js
- Estructura base del proyecto
- Configuración de Tailwind CSS
- Componentes básicos de UI

## Convenciones de Versionado

Usamos [SemVer](https://semver.org/) para el versionado. Para las versiones disponibles, ver los [tags en este repositorio](https://github.com/tuusuario/rental-properties/tags).

### Formato de Versión

- MAJOR.MINOR.PATCH (ejemplo: 1.0.0)
  - MAJOR: Cambios incompatibles con versiones anteriores
  - MINOR: Nuevas funcionalidades compatibles con versiones anteriores
  - PATCH: Correcciones de errores compatibles con versiones anteriores

### Formato de Commit

Seguimos la convención de [Conventional Commits](https://www.conventionalcommits.org/):

- feat: Nueva funcionalidad
- fix: Corrección de error
- docs: Cambios en documentación
- style: Cambios de formato
- refactor: Refactorización de código
- test: Adición o modificación de tests
- chore: Cambios en el proceso de build o herramientas auxiliares

## Instrucciones para Mantener el Changelog

1. Agregar cambios en la sección [Unreleased]
2. Al crear una nueva versión:
   - Mover cambios de [Unreleased] a una nueva sección con la versión
   - Agregar la fecha de la versión
   - Crear un nuevo tag en git
   - Actualizar links de comparación de versiones

## Links

- [Unreleased]: https://github.com/tuusuario/rental-properties/compare/v1.1.0...HEAD
- [1.1.0]: https://github.com/tuusuario/rental-properties/releases/tag/v1.1.0
- [1.0.0]: https://github.com/tuusuario/rental-properties/releases/tag/v1.0.0
