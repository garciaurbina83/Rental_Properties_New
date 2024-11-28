# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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

### Changed
- Simplificación de la clase Settings
  - Migración de Pydantic a dataclasses para una validación más simple
  - Manejo consistente de variables de entorno en `__post_init__`
  - Mejora en la organización del código de configuración

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

- [Unreleased]: https://github.com/tuusuario/rental-properties/compare/v1.0.0...HEAD
- [1.0.0]: https://github.com/tuusuario/rental-properties/releases/tag/v1.0.0
