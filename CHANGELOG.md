# 📑 CHANGELOG

Todas las notas de cambios para el proyecto **DocsFlow Backend**.  
Formato basado en [SemVer](https://semver.org/) y [Conventional Commits](https://www.conventionalcommits.org/).  

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

