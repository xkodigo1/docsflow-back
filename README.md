# DocsFlow Backend

Sistema de gestión de documentos operativos con extracción automática de datos de PDFs.

## 🚀 Características

- **Autenticación JWT** con roles (admin/operador)
- **Subida y procesamiento de PDFs** con extracción de tablas
- **Control de acceso por departamento**
- **Búsqueda y exportación** de datos extraídos
- **Recuperación de contraseña** por email
- **Bloqueo automático** por intentos fallidos

## 📋 Requisitos

- Python 3.8+
- MySQL 8.0+
- Node.js (para frontend)

## 🛠️ Instalación

### 1. Clonar el repositorio
```bash
git clone <repository-url>
cd docs-flow/backend
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar base de datos
```bash
# Crear base de datos y tablas
mysql -u root -p < database/db_schema.sql
```

### 5. Configurar variables de entorno
Crear archivo `.env` en la raíz del backend:

```env
# Aplicación
APP_NAME=Docsflow
APP_ENV=development
APP_PORT=8000

# JWT
JWT_SECRET_KEY=tu_clave_secreta_muy_segura_aqui
JWT_ALGORITHM=HS256
JWT_EXPIRATIONS_MINUTES=30

# Base de datos
DB_USER=root
DB_PASSWORD=tu_password_mysql
DB_HOST=localhost
DB_PORT=3306
DB_NAME=docsflow

# Uploads
UPLOAD_DIRECTORY=./uploads

# SMTP (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
SMTP_USE_TLS=true
SENDER_EMAIL=tu_email@gmail.com
EMAIL_DEBUG=true

# Frontend
FRONTEND_BASE_URL=http://localhost:5174

# CORS
CORS_ALLOWED_ORIGINS=["http://localhost:5174"]
```

### 6. Ejecutar la aplicación
```bash
uvicorn app.main:application --reload --host 0.0.0.0 --port 8000
```

## 📚 API Endpoints

### 🔐 Autenticación

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|---------|
| POST | `/auth/login` | Iniciar sesión | Público |
| POST | `/auth/forgot-password` | Solicitar recuperación | Público |
| POST | `/auth/reset-password` | Restablecer contraseña | Público |
| POST | `/auth/register` | Registrar usuario | Admin |

### 👥 Usuarios

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|---------|
| GET | `/users/me` | Perfil actual | Autenticado |
| GET | `/users/` | Listar usuarios | Admin |

### 📄 Documentos

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|---------|
| POST | `/documents/upload` | Subir PDF | Autenticado |
| GET | `/documents/` | Listar documentos | Autenticado |
| GET | `/documents/{id}` | Ver documento | Autenticado |
| GET | `/documents/{id}/status` | Estado procesamiento | Autenticado |
| GET | `/documents/{id}/download` | Descargar PDF | Autenticado |
| POST | `/documents/{id}/process` | Procesar documento | Autenticado |
| POST | `/documents/{id}/reprocess` | Reprocesar documento | Autenticado |
| DELETE | `/documents/{id}` | Eliminar documento | Autenticado |
| GET | `/documents/search` | Buscar documentos | Autenticado |

### 📊 Tablas Extraídas

| Método | Endpoint | Descripción | Acceso |
|--------|----------|-------------|---------|
| GET | `/tables/{document_id}` | Ver tablas del documento | Autenticado |
| GET | `/tables/search` | Buscar en tablas | Autenticado |
| GET | `/tables/{document_id}/export` | Exportar a CSV | Autenticado |

## 🔑 Autenticación

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@docsflow.com",
    "password": "admin123"
  }'
```

### Usar token
```bash
curl -X GET "http://localhost:8000/users/me" \
  -H "Authorization: Bearer tu_jwt_token_aqui"
```

## 📤 Subir Documento

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Authorization: Bearer tu_jwt_token_aqui" \
  -F "file=@documento.pdf" \
  -F "document_type=factura" \
  -F "department_id=1"
```

## 🔍 Buscar en Tablas

```bash
curl -X GET "http://localhost:8000/tables/search?q=total&limit=10" \
  -H "Authorization: Bearer tu_jwt_token_aqui"
```

## 📊 Exportar a CSV

```bash
curl -X GET "http://localhost:8000/tables/1/export" \
  -H "Authorization: Bearer tu_jwt_token_aqui" \
  -o tablas_exportadas.csv
```

## 🏗️ Estructura del Proyecto

```
backend/
├── app/
│   ├── config/
│   │   └── settings.py          # Configuración de la app
│   ├── controllers/             # Endpoints de la API
│   │   ├── auth.py
│   │   ├── documents.py
│   │   ├── tables.py
│   │   └── users.py
│   ├── middlewares/
│   │   └── auth.py              # Middleware de autenticación
│   ├── repositories/            # Acceso a datos
│   │   ├── user_repo.py
│   │   ├── document_repo.py
│   │   ├── table_repo.py
│   │   └── department_repo.py
│   ├── schemas/                 # Modelos Pydantic
│   │   ├── user.py
│   │   ├── document.py
│   │   └── extracted_table.py
│   ├── services/                # Lógica de negocio
│   │   ├── auth_service.py
│   │   └── pdf_processing.py
│   ├── utils/                   # Utilidades
│   │   ├── db.py
│   │   ├── security.py
│   │   ├── email.py
│   │   └── files.py
│   └── main.py                  # Aplicación principal
├── database/
│   └── db_schema.sql            # Esquema de la base de datos
├── uploads/                     # Archivos subidos
├── requirements.txt
└── README.md
```

## 🔒 Seguridad

- **JWT** con expiración de 30 minutos
- **Bcrypt** para hash de contraseñas
- **Control de intentos fallidos** (5 intentos para operadores)
- **Acceso por departamento** (operadores solo ven su departamento)
- **Validación de archivos** (solo PDF, máximo 15MB)

## 🚨 Troubleshooting

### Error de conexión a BD
```bash
# Verificar que MySQL esté corriendo
mysql -u root -p -e "SHOW DATABASES;"

# Verificar variables de entorno
echo $DB_HOST $DB_USER $DB_NAME
```

### Error de permisos en uploads
```bash
# Crear directorio y dar permisos
mkdir -p uploads
chmod 755 uploads
```

### Error de email
- Verificar configuración SMTP en `.env`
- Usar App Password para Gmail
- Revisar logs con `EMAIL_DEBUG=true`

## 📝 Desarrollo

### Generar PDF de prueba
```bash
python scripts/generate_sample_pdf.py
```

### Ver logs de la aplicación
```bash
uvicorn app.main:application --reload --log-level debug
```

### Documentación interactiva
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🤝 Contribución

1. Fork el proyecto
2. Crear rama feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver `LICENSE` para más detalles.
