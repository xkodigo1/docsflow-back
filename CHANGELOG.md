# 📑 CHANGELOG

Todas las notas de cambios para el proyecto **DocsFlow Backend**.  
Formato basado en [SemVer](https://semver.org/) y [Conventional Commits](https://www.conventionalcommits.org/).  

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

