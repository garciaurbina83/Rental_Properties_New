# SSL Configuration

Este directorio contiene los certificados SSL/TLS para el servidor Nginx.

## Requisitos de SSL

Para habilitar HTTPS, necesitas:

1. **Certificado SSL** (`server.crt`)
   - Certificado público
   - Formato PEM
   - Cadena completa de certificados si es necesario

2. **Clave Privada** (`server.key`)
   - Clave privada del certificado
   - Formato PEM
   - Sin contraseña

## Obtener Certificados

### Opción 1: Let's Encrypt (Recomendado para Producción)

1. Instalar Certbot:
```bash
apt-get update
apt-get install certbot python3-certbot-nginx
```

2. Obtener certificado:
```bash
certbot --nginx -d tudominio.com
```

3. Los certificados se generarán automáticamente en:
   - `/etc/letsencrypt/live/tudominio.com/fullchain.pem`
   - `/etc/letsencrypt/live/tudominio.com/privkey.pem`

4. Copiar certificados a este directorio:
```bash
cp /etc/letsencrypt/live/tudominio.com/fullchain.pem ./server.crt
cp /etc/letsencrypt/live/tudominio.com/privkey.pem ./server.key
```

### Opción 2: Certificado Auto-firmado (Solo Desarrollo)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout server.key \
  -out server.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
```

## Estructura de Archivos

```
ssl/
├── server.crt     # Certificado público
├── server.key     # Clave privada
└── README.md      # Esta documentación
```

## Configuración en Nginx

La configuración SSL ya está incluida en `../conf.d/default.conf`:

```nginx
server {
    listen 443 ssl;
    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;
    
    # Configuraciones de seguridad SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
}
```

## Notas de Seguridad

1. **Permisos**
   - Certificado (`server.crt`): 644 (-rw-r--r--)
   - Clave privada (`server.key`): 600 (-rw-------)

2. **Renovación**
   - Let's Encrypt: Configurar renovación automática
   - Certificados auto-firmados: Regenerar antes de expirar

3. **Respaldo**
   - Mantener copias seguras de las claves privadas
   - Documentar proceso de renovación

4. **Monitoreo**
   - Configurar alertas para expiración de certificados
   - Verificar regularmente la validez de los certificados

## Pruebas

Verificar la configuración SSL:
```bash
openssl s_client -connect localhost:443 -servername localhost
```

## Troubleshooting

1. **Error de certificado no encontrado**
   - Verificar rutas en nginx.conf
   - Verificar permisos de archivos

2. **Certificado expirado**
   - Renovar con Let's Encrypt
   - Regenerar certificado auto-firmado

3. **Problemas de cadena de certificados**
   - Verificar orden en server.crt
   - Incluir certificados intermedios
