# 🌳 Flujo de Trabajo con Git Flow en DocsFlow

Este documento explica cómo se trabajará con **Git Flow** en el proyecto **DocsFlow**.  
El objetivo es mantener un flujo claro de ramas y commits, evitando conflictos y asegurando releases ordenados.

---

## 🔧 Inicializar Git Flow

Antes de comenzar, debes inicializar Git Flow en tu repositorio:

```bash
git flow init
```

👉 Este comando creará la estructura básica de ramas:

- `main` → código en producción.  
- `develop` → integración de features en desarrollo.  

---

## ✨ Trabajando con una nueva Feature

1. Crear la rama de feature:

   ```bash
   git flow feature start nombre-feature
   ```

2. Trabajar normalmente en esa rama.  

   - Agregar cambios.  

   - Hacer commits siguiendo **Conventional Commits**:

     ```bash
     git commit -m "feat(auth): implementar login con JWT 🔑"
     ```

3. Finalizar la feature:

   ```bash
   git flow feature finish nombre-feature
   ```

4. Subir los cambios a remoto:

   ```bash
   git push origin develop
   ```

---

## 🚀 Crear un Release (pasar de `develop` a `main`)

1. Crear rama de release:

   ```bash
   git flow release start v1.0.0
   ```

2. Asegúrate de haber hecho commit con los últimos cambios en la release.  

3. Finalizar el release (fusiona con `main` y `develop`):

   ```bash
   git flow release finish v1.0.0
   ```

4. Subir cambios y tags:

   ```bash
   git push origin develop
   git push origin main --tags
   ```

---

## 🔥 Crear un Hotfix (corrección en producción)

Cuando aparece un error crítico en producción:

1. Crear la rama de hotfix:

   ```bash
   git flow hotfix start v1.0.1
   ```

2. Realizar los cambios necesarios y commitear:

   ```bash
   git commit -m "fix(auth): corregir validación de token inválido 🐛"
   ```

3. Finalizar el hotfix (fusiona con `main` y `develop`):

   ```bash
   git flow hotfix finish v1.0.1
   ```

4. Subir los cambios a remoto:

   ```bash
   git push origin develop
   git push origin main --tags
   ```

---

## ✅ Buenas prácticas en DocsFlow

- Una rama = una tarea (issue en Jira).  
- Commits pequeños y frecuentes usando **Conventional Commits + gitmojis**.  
- Nunca trabajar directo en `main` ni en `develop`.  
- Siempre usar `git flow` para crear, terminar y fusionar ramas.  
- Hacer **Pull Requests** para revisiones de código antes de mergear.  