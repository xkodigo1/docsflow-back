# 📦 Backend - DocsFlow

Este es el **backend de DocsFlow**, desarrollado con **Python 3.11+**, **FastAPI** y **MySQL**.  
Aquí encontrarás las instrucciones necesarias para instalar dependencias, configurar el entorno y ejecutar el proyecto.

---

## 🚀 Requisitos previos
- [Python 3.11+](https://www.python.org/downloads/)
- [MySQL 8+](https://dev.mysql.com/downloads/)
- [Git](https://git-scm.com/)

---

## 1. Crear entorno virtual
```bash
python3 -m venv venv
source venv/bin/activate (Linux / macOS)
.\venv\Scripts\activate (Windows)
```

## 2. Instalar dependencias
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
## 3. Configuración de Base de Datos
```bash
DB_HOST=localhost
DB_PORT=3306
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=docsflow_db
```

## 4. Ejecutar el servidor
```bash
fastapi dev main.py
```
**Por defecto estará disponible en:**
    
    http://127.0.0.1:8000   

**Documentación automática:**
    
    Swagger UI → http://127.0.0.1:8000/docs
    Redoc → http://127.0.0.1:8000/redoc

## ✅ Listo

Con esto deberías **poder levantar el backend** localmente.

Si algo falla, revisa que:

    1. Tu base de datos MySQL esté corriendo.
    2. Las credenciales en .env sean correctas.
    3. Estés dentro del entorno virtual antes de instalar dependencias o correr el servidor.