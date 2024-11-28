# Docker Configuration

Este directorio contiene toda la configuración de Docker para el proyecto Rental Properties.

## Estructura del Proyecto

```
docker/
├── backend/           # Configuración Docker del backend
│   ├── Dockerfile
│   └── docker-entrypoint.sh
├── frontend/         # Configuración Docker del frontend
│   └── Dockerfile
├── monitoring/       # Configuración de monitoreo
│   ├── prometheus/
│   └── alertmanager/
├── nginx/           # Configuración del proxy reverso
│   ├── conf.d/
│   └── ssl/
├── docker-compose.yml           # Composición principal
└── docker-compose.monitoring.yml # Composición de monitoreo
```

## Servicios

### Principales (docker-compose.yml)

1. **Backend (API)**
   - FastAPI
   - Puerto: 8000
   - Dependencias: PostgreSQL, Redis

2. **Frontend**
   - React
   - Puerto: 3000
   - Build multi-etapa con Nginx

3. **PostgreSQL**
   - Versión: 15
   - Puerto: 5432
   - Volumen persistente

4. **Redis**
   - Versión: 7
   - Puerto: 6379
   - Volumen persistente

5. **Nginx**
   - Proxy reverso
   - Puertos: 80, 443
   - SSL/TLS

### Monitoreo (docker-compose.monitoring.yml)

1. **Prometheus**
   - Métricas y alertas
   - Puerto: 9090

2. **Alertmanager**
   - Gestión de alertas
   - Puerto: 9093

3. **Node Exporter**
   - Métricas del sistema
   - Puerto: 9100

4. **Grafana**
   - Visualización
   - Puerto: 3000

## Uso

1. Desarrollo local:
```bash
docker-compose up -d
```

2. Monitoreo:
```bash
docker-compose -f docker-compose.monitoring.yml up -d
```

3. Logs:
```bash
# Ver logs de un servicio
docker-compose logs -f [servicio]

# Ver logs de todos los servicios
docker-compose logs -f
```

4. Reconstruir servicios:
```bash
docker-compose up -d --build
```

## Redes

- **app-network**: Red principal para comunicación entre servicios
- **monitoring**: Red para servicios de monitoreo

## Volúmenes

- **postgres_data**: Datos de PostgreSQL
- **redis_data**: Datos de Redis
- **prometheus_data**: Datos de Prometheus

## Notas de Seguridad

1. Nunca commitear archivos .env
2. Usar secrets para credenciales en producción
3. Mantener las imágenes base actualizadas
4. Escanear imágenes por vulnerabilidades
