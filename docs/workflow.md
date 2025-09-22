# 🚀 Flujo de Trabajo con Ramas y Commits en DocsFlow

Este documento describe el flujo de trabajo recomendado con **Git Flow**, ramas y commits para el desarrollo del proyecto **DocsFlow**.  

---

## 1. Preparación inicial

1. Clonar repo e inicializar Git Flow:

   ```bash
   git clone https://github.com/xkodigo1/fullstack-project.git
   cd docsflow
   git flow init
   ```

👉 Esto crea las ramas principales:

- `main` (producción)  
- `develop` (desarrollo)  

---

## 2. Desarrollo de una Feature

### Crear una rama de feature

```bash
git checkout develop
git pull origin develop
git flow feature start auth-login
```

### Trabajar en la feature

- Hacer cambios en el código.  

- Guardar progreso con commits pequeños y descriptivos:

  ```bash
  git add .
  git commit -m "feat(auth): implementar endpoint login con JWT 🔑"
  git commit -m "feat(auth): agregar validación de intentos fallidos 🚨"
  ```

👉 Siempre usar **Conventional Commits**:

- `feat`: nueva funcionalidad  
- `fix`: corrección de error  
- `docs`: documentación  
- `chore`: cambios menores  
- `refactor`, `perf`, `test`, etc.  

### Finalizar la feature

```bash
git flow feature finish auth-login
```

👉 Esto hace merge automático a `develop`.  

### Subir cambios a remoto

```bash
git push origin develop
```

---

## 3. Aplicar un Hotfix

Si aparece un bug crítico en producción:

```bash
git flow hotfix start v0.2.1
```

- Hacer cambios y commits:

  ```bash
  git commit -m "fix(auth): resolver bug en refresh token 🔄"
  ```

Finalizar el hotfix:

```bash
git flow hotfix finish v0.2.1
```

Subir al remoto:

```bash
git push origin develop
git push origin main --tags
```

---

## 4. Resumen visual del flujo

```
main
  └── develop
       ├── feature/auth-login
       ├── feature/user-crud
       ├── feature/pdf-upload
       └── hotfix/v0.2.1
```

---

## ✅ Buenas prácticas

- Commits pequeños y frecuentes usando **Conventional Commits + gitmojis**.  
- Nunca commitear directo a `main` ni a `develop`.  
- Siempre usar `git flow` para crear, terminar y fusionar ramas.  
- Pull Requests para revisión antes de mergear.  