# Frontend Service

Aplicación frontend de Rental Properties construida con React, TypeScript y Material-UI.

## Estructura del Proyecto

```
frontend/
├── src/
│   ├── components/     # Componentes reutilizables
│   ├── pages/         # Vistas principales
│   ├── services/      # Llamadas a la API
│   ├── context/       # Gestión de estado global
│   ├── hooks/         # Hooks personalizados
│   └── utils/         # Funciones auxiliares
└── public/            # Archivos estáticos
```

## Tecnologías Principales

- React 18
- TypeScript 4
- Material-UI 5
- React Query
- Zustand (Estado global)
- Clerk (Autenticación)
- Axios (Cliente HTTP)
- Recharts (Gráficos)

## Configuración

1. Instalar dependencias:
```bash
npm install
```

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

## Desarrollo

1. Iniciar servidor de desarrollo:
```bash
npm start
```

2. Construir para producción:
```bash
npm run build
```

## Tests

```bash
# Ejecutar tests
npm test

# Ejecutar tests con coverage
npm test -- --coverage
```

## Docker

El servicio está containerizado. Para ejecutar con Docker:
```bash
cd ../docker
docker-compose up -d
```

## Características Principales

1. **Autenticación**
   - Login/Registro con Clerk
   - Protección de rutas
   - Manejo de tokens

2. **Gestión de Propiedades**
   - CRUD de propiedades
   - Filtrado y búsqueda
   - Visualización en lista y grid

3. **Gestión de Inquilinos**
   - CRUD de inquilinos
   - Historial de pagos
   - Documentos asociados

4. **Dashboard**
   - Resumen de ingresos
   - Ocupación de propiedades
   - Gráficos y estadísticas

5. **Optimizaciones**
   - Lazy loading de componentes
   - Caching con React Query
   - Componentes reutilizables
