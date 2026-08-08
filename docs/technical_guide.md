# 🔧 Guía Técnica - Nexora Labs Medic Center

Esta guía está destinada a administradores de sistemas y desarrolladores responsables del despliegue, mantenimiento y extensión de Nexora Labs Medic Center.

## 🏗️ 1. Arquitectura del Sistema

Nexora Labs Medic Center sigue una arquitectura modular basada en microservicios contenerizados:

- **Frontend:** Flutter Web (Compilado a JS/WASM), servido vía Nginx.
- **Backend:** FastAPI (Python 3.10+), ejecutado en Uvicorn.
- **Base de Datos:** PostgreSQL 14+ con extensiones para búsqueda full-text.
- **Caché:** Redis (Opcional, para sesiones y colas).
- **Infraestructura:** Docker & Docker Compose para orquestación.

### Diagrama de Flujo de Datos
```
[Cliente/Navegador] <-> [Nginx (SSL Termination)] <-> [FastAPI Backend]
                                                        |
                                                        v
                                                [PostgreSQL DB]
                                                        ^
                                                        |
                                                [Redis Cache]
```

## 🚀 2. Despliegue en Producción

### Prerrequisitos del Servidor
- SO: Ubuntu 22.04 LTS o Debian 11+.
- RAM: Mínimo 4GB (Recomendado 8GB).
- CPU: 2 vCPU cores.
- Disco: 20GB libres mínimo.
- Software: Docker Engine 20+, Docker Compose v2+.

### Paso a Paso para Instalación

#### 1. Clonar y Configurar
```bash
git clone https://github.com/Javitonito-Javier/clinicapharma.git
cd clinicapharma
cp .env.example .env
```

#### 2. Generar Credenciales Seguras
Ejecuta los siguientes comandos para generar claves únicas:
```bash
# Clave Secreta para JWT
python3 -c "import secrets; print(secrets.token_urlsafe(64))"

# Contraseña de Base de Datos
openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 20; echo ""
```
Pega estos valores en tu archivo `.env`.

#### 3. Ajustar Variables Críticas (.env)
Asegúrate de configurar correctamente:
- `SECRET_KEY`: La cadena larga generada arriba.
- `DATABASE_URL`: Usa `postgresql://user:pass@db:5432/dbname` (Nota el host `db`, no localhost).
- `ENVIRONMENT`: Debe ser `production`.

#### 4. Desplegar Contenedores
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

#### 5. Verificar Estado
```bash
docker compose ps
docker compose logs -f backend
```
Deberías ver "Application startup complete" en los logs.

## 🛡️ 3. Seguridad y Hardening

### Firewall (UFW)
Solo abre los puertos estrictamente necesarios:
```bash
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP (Para Let's Encrypt)
sudo ufw allow 443/tcp  # HTTPS
sudo ufw enable
```

### SSL/TLS (HTTPS)
Se recomienda usar **Certbot** con Nginx Proxy Manager o Traefik incluido en el stack.
No expongas el sistema directamente a internet sin HTTPS.

### Backups Automáticos
El script `scripts/backup_db.sh` se encarga de respaldar la base de datos.
Configura un cron job para ejecutarlo diariamente:
```bash
# Editar crontab
crontab -e

# Agregar línea (Backup diario a las 3 AM)
0 3 * * * /path/to/clinicapharma/scripts/backup_db.sh
```

## 🔍 4. Troubleshooting Común

| Problema | Causa Probable | Solución |
|----------|----------------|----------|
| **Error 502 Bad Gateway** | El backend no arrancó | Revisa `docker compose logs backend`. Suele ser error en `.env` o DB. |
| **Connection Refused DB** | Host incorrecto en `DATABASE_URL` | Asegúrate de usar `@db:` y no `@localhost:` dentro de Docker. |
| **Lentitud General** | Falta de índices o RAM | Verifica logs de Postgres. Considera aumentar RAM del servidor. |
| **Sesiones que caducan rápido** | `SECRET_KEY` cambiada o inválida | Regenera la clave y reinicia contenedores. |

## 🧪 5. Mantenimiento y Actualizaciones

### Actualizar el Código
```bash
cd /path/to/clinicapharma
git pull origin main
docker compose -f docker-compose.prod.yml up -d --build
```
*El sistema realizará migraciones de base de datos automáticamente al iniciar.*

### Restaurar Backup
```bash
# Detener sistema
docker compose down

# Restaurar DB
gunzip < backup_YYYYMMDD.sql.gz | psql -h localhost -U usuario -v ON_ERROR_STOP=1 nombre_db

# Reiniciar
docker compose up -d
```

## 📈 6. Escalabilidad

Si la clínica crece y necesitas más rendimiento:
1. **Base de Datos:** Mueve PostgreSQL a un servidor dedicado o servicio gestionado (RDS).
2. **Backend:** Levanta múltiples réplicas del contenedor `backend` detrás de un Load Balancer.
3. **Frontend:** Sirve los archivos estáticos desde un CDN.

---
*Para contribuciones de código, lee las reglas en `docs/coding-rules.md`.*
