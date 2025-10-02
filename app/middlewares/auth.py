from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.config.settings import settings

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return {
            "id": int(payload.get("sub")),
            "role": payload.get("role"),
            "department_id": payload.get("department_id")
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")