from fastapi import APIRouter, Depends, HTTPException
from typing import List
from utils.authz import require_admin
from repositories.department_repo import (
    get_all_departments,
    get_department_by_id,
    create_department,
    update_department,
    delete_department,
    get_department_stats
)
from schemas.department import DepartmentCreate, DepartmentOut

router = APIRouter(prefix="/departments", tags=["departments"])

@router.get("/", response_model=List[DepartmentOut])
def get_departments(admin=Depends(require_admin)):
    """Obtener todos los departamentos"""
    return get_all_departments()

@router.get("/{department_id}", response_model=DepartmentOut)
def get_department(department_id: int, admin=Depends(require_admin)):
    """Obtener un departamento por ID"""
    department = get_department_by_id(department_id)
    if not department:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")
    return department

@router.post("/", response_model=DepartmentOut)
def create_department_endpoint(department_data: DepartmentCreate, admin=Depends(require_admin)):
    """Crear un nuevo departamento"""
    try:
        return create_department(department_data.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{department_id}", response_model=DepartmentOut)
def update_department_endpoint(
    department_id: int, 
    department_data: DepartmentCreate, 
    admin=Depends(require_admin)
):
    """Actualizar un departamento"""
    try:
        return update_department(department_id, department_data.name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=404, detail="Departamento no encontrado")

@router.delete("/{department_id}")
def delete_department_endpoint(department_id: int, admin=Depends(require_admin)):
    """Eliminar un departamento y toda la información relacionada (eliminación en cascada)"""
    try:
        result = delete_department(department_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/stats/summary")
def get_department_stats_endpoint(admin=Depends(require_admin)):
    """Obtener estadísticas de departamentos"""
    return get_department_stats()

@router.get("/{department_id}/stats")
def get_department_detailed_stats(department_id: int, admin=Depends(require_admin)):
    """Obtener estadísticas detalladas de un departamento específico"""
    from repositories.department_repo import get_department_detailed_stats
    return get_department_detailed_stats(department_id)
