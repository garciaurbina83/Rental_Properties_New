# Guía de Inicio - Frontend Rental Properties

## Requisitos Previos

- Node.js 16+ 
- npm o yarn
- Cuenta en Clerk (para autenticación)

## Configuración Inicial

1. **Instalación de Dependencias**
```bash
npm install
```

2. **Variables de Entorno**
Copia `.env.example` a `.env.local` y configura las variables necesarias:
```bash
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=tu_clerk_publishable_key
CLERK_SECRET_KEY=tu_clerk_secret_key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

3. **Iniciar el Servidor de Desarrollo**
```bash
npm run dev
```

## Estructura del Proyecto

```
frontend-next/
├── src/
│   ├── app/          # Páginas y rutas de la aplicación
│   ├── components/   # Componentes reutilizables
│   ├── hooks/        # Custom hooks
│   ├── lib/          # Utilidades y configuraciones
│   ├── styles/       # Estilos globales y configuración de Tailwind
│   └── types/        # Definiciones de tipos TypeScript
├── public/           # Archivos estáticos
├── docs/            # Documentación
└── tests/           # Tests unitarios y E2E
```

## Scripts Disponibles

- `npm run dev`: Inicia el servidor de desarrollo
- `npm run build`: Construye la aplicación para producción
- `npm run start`: Inicia el servidor de producción
- `npm run lint`: Ejecuta el linter
- `npm test`: Ejecuta los tests unitarios
- `npm run test:e2e`: Ejecuta los tests E2E
- `npm run test:coverage`: Genera reporte de cobertura de tests

## Convenciones de Código

### Nombrado de Archivos
- Componentes: PascalCase (ej. `PropertyCard.tsx`)
- Hooks: camelCase con prefijo "use" (ej. `useProperties.ts`)
- Utilidades: camelCase (ej. `formatCurrency.ts`)

### Imports
1. Imports de React/Next.js
2. Imports de librerías externas
3. Imports de componentes propios
4. Imports de tipos
5. Imports de estilos

### Componentes
- Un componente por archivo
- Usar TypeScript para props
- Implementar error boundaries cuando sea necesario
- Documentar props complejas

### Estado y Efectos
- Preferir hooks personalizados para lógica reutilizable
- Usar React Query para estado del servidor
- Implementar manejo de errores consistente

## Guías de Estilo

### TypeScript
- Usar tipos explícitos para props de componentes
- Evitar `any`
- Utilizar interfaces para objetos complejos
- Documentar tipos complejos

### CSS/Tailwind
- Usar clases de utilidad de Tailwind
- Componentes con estilos consistentes
- Seguir sistema de diseño establecido

## Testing

### Tests Unitarios
- Tests para componentes críticos
- Tests para hooks personalizados
- Mocks para servicios externos

### Tests E2E
- Flujos críticos de usuario
- Casos de error comunes
- Performance testing

## Deployment

1. **Preparación**
   - Verificar variables de entorno
   - Ejecutar tests
   - Verificar build local

2. **Proceso**
   - Build de producción
   - Verificación de assets
   - Deployment a plataforma elegida

## Troubleshooting

### Problemas Comunes
1. **Errores de Build**
   - Verificar dependencias
   - Limpiar cache de Next.js
   - Verificar tipos TypeScript

2. **Problemas de Autenticación**
   - Verificar configuración de Clerk
   - Revisar tokens y permisos

3. **Problemas de Rendimiento**
   - Analizar bundle size
   - Verificar lazy loading
   - Revisar re-renders innecesarios
