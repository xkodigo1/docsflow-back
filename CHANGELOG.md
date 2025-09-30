# 📑 CHANGELOG

Todas las notas de cambios para el proyecto **DocsFlow Backend**.  
Formato basado en [SemVer](https://semver.org/) y [Conventional Commits](https://www.conventionalcommits.org/).  

---

## 🎉 v1.0.1 – Release Final - Backend Completo  
**Fecha:** 2025-09-30  

### 🎯 Objetivo
**RELEASE FINAL** - El backend de DocsFlow cumple completamente con todos los requerimientos del proyecto. Sistema de gestión de documentos operativos con extracción automática, autenticación robusta, control de acceso por departamento y documentación completa.

---

### 🏆 Funcionalidades Completadas

#### 🔐 **Autenticación y Seguridad**
- ✅ **JWT con expiración de 30 minutos** y refresh tokens seguros
- ✅ **Recuperación de contraseña por email** con tokens de 15 minutos
- ✅ **Bloqueo automático** por 5 intentos fallidos (solo operadores)
- ✅ **Control de acceso por rol** (admin/operador) y departamento
- ✅ **Hash seguro de contraseñas** con bcrypt

#### 📄 **Gestión de Documentos**
- ✅ **Subida de PDFs** con validación (máximo 15MB)
- ✅ **Procesamiento automático** con extracción real de texto y tablas
- ✅ **Estados de procesamiento** (pending, processing, processed, error)
- ✅ **Control de acceso por departamento** (operadores ven solo su departamento)
- ✅ **Filtros por tipo de documento** y búsqueda por nombre
- ✅ **Descarga de documentos** originales
- ✅ **Re-procesamiento** de documentos

#### 📊 **Extracción y Análisis de Datos**
- ✅ **Extracción real de tablas** desde PDFs con `pdfplumber`
- ✅ **Detección de headers** y normalización de celdas
- ✅ **Búsqueda en contenido extraído** con `JSON_SEARCH`
- ✅ **Exportación a CSV** de tablas extraídas
- ✅ **Múltiples tablas por página** soportadas

#### 👥 **Gestión de Usuarios**
- ✅ **Registro de usuarios** (solo admin)
- ✅ **Listado de usuarios** con filtros por rol y departamento
- ✅ **Perfil de usuario** autenticado
- ✅ **Asignación por defecto a operador** en registro

#### 🗄️ **Base de Datos**
- ✅ **Esquema normalizado** con 5 tablas principales
- ✅ **Relaciones FK** y índices optimizados
- ✅ **Datos iniciales** (admin, departamentos)
- ✅ **Conexión persistente** integrada en FastAPI

#### 📚 **Documentación y API**
- ✅ **Swagger UI completo** con ejemplos y descripciones
- ✅ **README detallado** con configuración y ejemplos
- ✅ **Documentación de endpoints** con parámetros y respuestas
- ✅ **Ejemplos de uso** con curl

#### 🔧 **Arquitectura y Mantenibilidad**
- ✅ **Arquitectura en capas** (controllers, services, repositories, utils)
- ✅ **Separación de responsabilidades** clara
- ✅ **Utilidades reutilizables** (db, security, email, files)
- ✅ **Manejo de errores** robusto
- ✅ **CORS configurado** para frontend

#### 🧪 **Testing y Calidad**
- ✅ **PDF de prueba comprehensivo** (3 páginas, múltiples tablas)
- ✅ **Datos de prueba realistas** (facturas, reportes, análisis)
- ✅ **Validación de linter** sin errores
- ✅ **Estructura de proyecto** organizada

---

### 📋 **Endpoints Completos**

#### 🔓 **Públicos**
- `POST /auth/login` - Iniciar sesión
- `POST /auth/forgot-password` - Recuperación de contraseña
- `POST /auth/reset-password` - Restablecer contraseña

#### 🔐 **Privados (requiere token)**
- `GET /users/me` - Perfil actual
- `GET /users/` - Listar usuarios (admin)
- `POST /auth/register` - Registrar usuario (admin)
- `POST /documents/upload` - Subir PDF
- `GET /documents/` - Listar documentos
- `GET /documents/{id}` - Ver documento
- `GET /documents/{id}/status` - Estado de procesamiento
- `GET /documents/{id}/download` - Descargar PDF
- `POST /documents/{id}/process` - Procesar documento
- `POST /documents/{id}/reprocess` - Reprocesar documento
- `DELETE /documents/{id}` - Eliminar documento
- `GET /documents/search` - Buscar documentos
- `GET /tables/{document_id}` - Ver tablas del documento
- `GET /tables/search` - Buscar en tablas
- `GET /tables/{document_id}/export` - Exportar a CSV

---

### 🎯 **Cumplimiento de Requerimientos**

#### ✅ **Requerimientos Técnicos**
- ✅ Backend funcional con endpoints protegidos
- ✅ Autenticación completa con JWT y recuperación por email
- ✅ Procesamiento de PDF y almacenamiento estructurado
- ✅ Documentación de endpoints con ejemplos en Swagger
- ✅ Entrega organizada con README backend

#### ✅ **Requerimientos Funcionales**
- ✅ Gestión de usuarios con roles diferenciados
- ✅ Subida y procesamiento automático de PDFs
- ✅ Extracción de tablas y datos clave
- ✅ Búsqueda y visualización por departamento
- ✅ Seguridad con roles y control de acceso
- ✅ Expiración de sesión por inactividad (30 min)
- ✅ Bloqueo por intentos fallidos (5 intentos para operadores)

#### ✅ **Requerimientos de Seguridad**
- ✅ JWT con expiración de 30 minutos
- ✅ Control de 5 intentos fallidos para operadores
- ✅ Admin no se bloquea
- ✅ Token único por email para recuperación
- ✅ Acceso por departamento (operadores solo ven su departamento)

---

### 🚀 **Estado Final**
**El backend de DocsFlow está COMPLETO y listo para producción.**  
Todos los requerimientos han sido implementados, probados y documentados.  
El sistema está preparado para integrarse con el frontend React + TypeScript.

---

## 🚀 v0.3.0 – Extracción real de PDFs, Búsquedas y Recuperación por Email  
**Fecha:** 2025-09-30  

### 🎯 Objetivo
Agregar extracción real de contenido desde PDFs, endpoints de consulta/búsqueda de tablas, flujo de recuperación de contraseña por correo y refactor hacia repos/servicios y utilidades reutilizables.

---

### 📦 Cambios incluidos
- :mag: **Extracción real de PDFs**
  - Servicio `app/services/pdf_processing.py` con `pdfplumber` (texto y tablas).
  - Documentación de proceso: `docs/pdf_processing.md`.
- :sparkles: **Endpoints de tablas**
  - `GET /tables/{document_id}` → lista tablas extraídas del documento (control de acceso por rol/departamento).
  - `GET /tables/search?q=` → búsqueda en JSON de tablas (`JSON_SEARCH`) unida a `documents`; respuesta diferenciada `{ document, table }`.
- :lock: **Recuperación de contraseña por email (SMTP)**
  - `POST /auth/forgot-password` → genera token (15 min) y envía enlace por correo.
  - `POST /auth/reset-password` → valida token y actualiza contraseña.
  - Config SMTP en `settings.py` (Gmail/Office365), utilidad `utils/email.py` con TLS/SSL fallback y `EMAIL_DEBUG`.
- :closed_lock_with_key: **Seguridad y autorización**
  - Bloqueo de operador por 5 intentos fallidos (centralizado en `services/auth_service.py` y `repositories/user_repo.py`).
  - Dependencias `require_admin` y helpers `ensure_user_can_access_document` en `utils/authz.py`.
- :package: **Refactor repos/utilidades**
  - Repos: `document_repo.py`, `table_repo.py`, `department_repo.py`, `password_reset_repo.py`.
  - Utilidades: `utils/files.py` (rutas/escritura uploads), `utils/query.py` (WHERE/PAGINACIÓN).
  - Controllers `documents.py` y `tables.py` refactorizados a usar repos/utilidades.
- :busts_in_silhouette: **Usuarios**
  - `GET /users/` (solo admin) con parámetros opcionales; por defecto lista `role='operador'`.
  - `GET /users/me` → retorna datos del usuario desde el JWT.
- :gear: **Configuración**
  - `frontend_base_url` para construir enlaces de reset.
  - Carpeta `database/` con `db_schema.sql` (migrado desde `docs/`).
  - Script `scripts/generate_sample_pdf.py` y muestra `samples/sample_invoice.pdf`.

---

### ✅ Estado actual
- Extracción y persistencia de texto/tablas desde PDFs funcionando.
- Búsqueda por contenido extraído disponible y separada de la búsqueda por documentos.
- Flujo completo de recuperación de contraseña por email (tokens de un solo uso, expirables).
- Control de acceso por rol/departamento centralizado y probado en endpoints de documentos/tablas.
- Repositorios y utilidades reducen duplicación y mejoran mantenibilidad.

---

## 🚀 v0.2.0 – Documents MVP  
**Fecha:** 2025-09-25  

### 🎯 Objetivo
Implementar el módulo de gestión de documentos (MVP), permitiendo a los usuarios subir, listar, consultar, procesar y eliminar PDFs con control de acceso por rol y departamento.  

---

### 📦 Cambios incluidos
- :sparkles: **documents-routes** – endpoints principales:  
  - `POST /documents/upload` → valida PDF, guarda en `uploads/` por departamento, inserta metadata (`status=pending`).  
  - `GET /documents/` → listado con paginación y filtros; operadores ven solo documentos de su departamento.  
  - `GET /documents/{id}` → detalle con control de acceso por rol/departamento.  
  - `DELETE /documents/{id}` → borra archivo físico y registro en DB con control de acceso.  
  - `POST /documents/{id}/process` → simula extracción, inserta datos en `extracted_tables`, marca documento como `processed`.  

- :gear: **main.py** – integración del router de documentos (`include_router(documents_router)`).  

---

### ✅ Estado actual
- Los usuarios pueden subir PDFs y gestionarlos desde la API.  
- Los operadores están restringidos a ver solo los documentos de su propio departamento.  
- Simulación de procesamiento implementada (persistencia en `extracted_tables`).  
- Documentos con estados básicos: `pending` y `processed`.  

---

## 🚀 v0.1.0 – Setup, Base, Auth & Users  
**Fecha:** 2025-09-23  

### 🎯 Objetivo
Levantar el servidor con conexión a base de datos MySQL, configuración de JWT y primeros endpoints de autenticación y gestión de usuarios.  

---

### 🔧 Setup & Base
- :tada: **project-setup** – estructura inicial del proyecto (MVC).  
- :sparkles: **app-instance** – instancia de FastAPI (`main.py`) con endpoint base `/`.  
- :gear: **config-env** – configuración de variables de entorno con `settings.py` y `.env`.  
- :sparkles: **db-connection** – conexión a MySQL integrada en ciclo de vida de FastAPI.  
- :card_file_box: **db-models** – script SQL (`docs/db_schema.sql`) con tablas normalizadas.  
- :package: **db-schemas** – esquemas Pydantic para usuarios, departamentos, documentos, tablas extraídas y tokens.  
- :closed_lock_with_key: **security-utils** – utilidades de seguridad (bcrypt para contraseñas, JWT utils).  

---

### 🔐 Autenticación & Usuarios
- :closed_lock_with_key: **auth-routes** – endpoints:  
  - `POST /auth/login` – login con JWT y bloqueo por intentos.  
  - `POST /auth/refresh` – refresh token seguro de un solo uso.  
  - `POST /auth/register` – registro de usuarios protegido solo para admins.  
- :busts_in_silhouette: **users-routes** – endpoints:  
  - `GET /users/me` – perfil del usuario autenticado.  
  - `GET /users` – listado de usuarios (solo admin).  
  - `DELETE /users/{id}` – eliminación de usuario (solo admin).  

---

### ✅ Estado actual
- Servidor FastAPI funcional (`uvicorn app.main:app --reload`).  
- Conexión persistente a MySQL validada en `/db-status`.  
- Seguridad JWT configurada (login, refresh, registro).  
- Control de roles (`admin`, `operador`) funcionando en endpoints protegidos.  
- CRUD básico de usuarios operativo. 

