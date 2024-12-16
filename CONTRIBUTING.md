# Guía de Contribución

## Proceso de Desarrollo

1. **Branches**
   - `main`: Producción
   - `develop`: Desarrollo
   - `feature/*`: Nuevas funcionalidades
   - `bugfix/*`: Correcciones
   - `hotfix/*`: Correcciones urgentes en producción

2. **Commits**
   Seguimos [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   <tipo>[alcance opcional]: <descripción>

   [cuerpo opcional]

   [nota de pie opcional]
   ```

   Tipos de commit:
   - feat: Nueva funcionalidad
   - fix: Corrección de error
   - docs: Documentación
   - style: Formato
   - refactor: Refactorización
   - test: Tests
   - chore: Mantenimiento

3. **Pull Requests**
   - Crear desde feature branch a develop
   - Incluir descripción clara de los cambios
   - Referenciar issues relacionados
   - Asegurar que pasan todos los tests
   - Obtener al menos una revisión aprobada

## Actualización del Changelog

1. **Para Nuevos Cambios**
   - Agregar entrada en sección [Unreleased]
   - Seguir el formato establecido
   - Incluir detalles relevantes

2. **Para Nuevas Versiones**
   ```bash
   # 1. Actualizar versión en package.json
   npm version [major|minor|patch]

   # 2. Mover cambios de [Unreleased] a nueva sección en CHANGELOG.md
   # 3. Agregar fecha de versión
   # 4. Actualizar links de comparación

   # 5. Commit y tag
   git add CHANGELOG.md package.json
   git commit -m "chore: release vX.Y.Z"
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

## Estándares de Código

### Backend (Python)
- Seguir PEP 8
- Usar type hints
- Documentar funciones y clases
- Tests para nueva funcionalidad

### Frontend (TypeScript)
- Seguir ESLint config
- Componentes funcionales
- Props tipadas
- Tests para componentes

### Docker
- Imágenes multi-stage
- Optimizar capas
- Documentar variables de entorno

## CI/CD

1. **Pre-commit**
   - Linting
   - Formateo
   - Tests unitarios

2. **Pipeline**
   - Build
   - Tests
   - Análisis estático
   - Deploy (según ambiente)

## Reportar Issues

1. **Bug Reports**
   - Descripción clara
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots si aplica
   - Ambiente (OS, versiones, etc.)

2. **Feature Requests**
   - Descripción del problema
   - Solución propuesta
   - Alternativas consideradas
   - Contexto adicional

## Releases

1. **Preparación**
   - Actualizar CHANGELOG.md
   - Actualizar documentación
   - Verificar tests
   - Review de seguridad

2. **Proceso**
   - Merge a main
   - Tag de versión
   - Build y deploy
   - Anuncio de release

## Contacto

- **Bugs y Features**: Issues en GitHub
- **Seguridad**: security@tudominio.com
- **Otros**: team@tudominio.com
