# 📂 Estructura del Proyecto DocsFlow

Este documento explica la organización de carpetas y archivos en el **backend (FastAPI + MySQL)**.  
La idea es mantener una arquitectura **MVC extendida** (Model-View-Controller) con capas adicionales para claridad y mantenibilidad.

---

## ⚙️ Backend (FastAPI)

```
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── routes.py
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── schemas/
│   ├── utils/
│   └── middlewares/
├── requirements.txt
└── .env.example
```

### 🗂️ Explicación por carpeta/archivo

- **`main.py`** → Punto de entrada de la aplicación FastAPI. Monta routers, middlewares y configuración.  
- **`config.py`** → Carga de variables de entorno (.env). Contiene configuración global.  
- **`database.py`** → Configuración y conexión a la base de datos MySQL.  
- **`routes.py`** → Archivo central donde se registran los routers de los controladores.  

#### 📁 `controllers/`

Contiene los **endpoints** que FastAPI expone (C de MVC).  
Ejemplo:  

- `auth_controller.py` → `/auth/login`, `/auth/register`  
- `users_controller.py` → `/users/`  
- `documents_controller.py` → `/documents/upload`, `/documents/search`  

#### 📁 `services/`

Aquí va la **lógica de negocio**.  
Ejemplo:  

- `auth_service.py` → validación de credenciales, generación de tokens.  
- `pdf_service.py` → extracción de texto/tablas de PDFs.  

#### 📁 `repositories/`

Acceso a **base de datos con SQL directo**.  
Ejemplo:  

- `user_repo.py` → CRUD de usuarios en MySQL.  
- `document_repo.py` → CRUD y búsquedas de documentos.  

#### 📁 `models/`

Modelos internos (ej: dataclasses o representaciones de tablas).  

#### 📁 `schemas/`

Modelos de **Pydantic** para validar requests y responses.  
Ejemplo: `UserCreate`, `UserLogin`, `DocumentResponse`.  

#### 📁 `utils/`

Funciones auxiliares como hashing, JWT, validaciones.  

#### 📁 `middlewares/`

Middlewares de FastAPI (ejemplo: logging, CORS, control de sesiones).  