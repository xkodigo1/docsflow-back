from utils.db import get_db_connection
from typing import List, Optional, Dict, Any


def exists(department_id: int) -> bool:
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT 1 FROM departments WHERE id = %s", (department_id,))
        return cursor.fetchone() is not None
    finally:
        cursor.close()
        conn.close()


def get_all_departments() -> List[Dict[str, Any]]:
    """Obtener todos los departamentos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM departments ORDER BY name")
        rows = cursor.fetchall()
        return [{"id": row[0], "name": row[1]} for row in rows]
    finally:
        cursor.close()
        conn.close()


def get_department_by_id(department_id: int) -> Optional[Dict[str, Any]]:
    """Obtener un departamento por ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, name FROM departments WHERE id = %s", (department_id,))
        row = cursor.fetchone()
        if row:
            return {"id": row[0], "name": row[1]}
        return None
    finally:
        cursor.close()
        conn.close()


def create_department(name: str) -> Dict[str, Any]:
    """Crear un nuevo departamento"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar si ya existe un departamento con ese nombre
        cursor.execute("SELECT id FROM departments WHERE name = %s", (name,))
        if cursor.fetchone():
            raise ValueError("Ya existe un departamento con ese nombre")
        
        cursor.execute("INSERT INTO departments (name) VALUES (%s)", (name,))
        conn.commit()
        
        department_id = cursor.lastrowid
        return {"id": department_id, "name": name}
    finally:
        cursor.close()
        conn.close()


def update_department(department_id: int, name: str) -> Dict[str, Any]:
    """Actualizar un departamento"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar si el departamento existe
        cursor.execute("SELECT id FROM departments WHERE id = %s", (department_id,))
        if not cursor.fetchone():
            raise ValueError("Departamento no encontrado")
        
        # Verificar si ya existe otro departamento con ese nombre
        cursor.execute("SELECT id FROM departments WHERE name = %s AND id != %s", (name, department_id))
        if cursor.fetchone():
            raise ValueError("Ya existe otro departamento con ese nombre")
        
        cursor.execute("UPDATE departments SET name = %s WHERE id = %s", (name, department_id))
        conn.commit()
        
        return {"id": department_id, "name": name}
    finally:
        cursor.close()
        conn.close()


def delete_department(department_id: int) -> Dict[str, Any]:
    """Eliminar un departamento y toda la información relacionada (eliminación en cascada)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar si el departamento existe
        cursor.execute("SELECT id, name FROM departments WHERE id = %s", (department_id,))
        department = cursor.fetchone()
        if not department:
            raise ValueError("Departamento no encontrado")
        
        # Obtener estadísticas antes de eliminar
        cursor.execute("SELECT COUNT(*) FROM users WHERE department_id = %s", (department_id,))
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE department_id = %s", (department_id,))
        doc_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM extracted_tables et 
            JOIN documents d ON et.document_id = d.id 
            WHERE d.department_id = %s
        """, (department_id,))
        table_count = cursor.fetchone()[0]
        
        # Eliminar en cascada (en orden correcto para respetar foreign keys)
        # 1. Eliminar tablas extraídas de documentos del departamento
        cursor.execute("""
            DELETE et FROM extracted_tables et 
            JOIN documents d ON et.document_id = d.id 
            WHERE d.department_id = %s
        """, (department_id,))
        
        # 2. Eliminar documentos del departamento
        cursor.execute("DELETE FROM documents WHERE department_id = %s", (department_id,))
        
        # 3. Eliminar usuarios del departamento
        cursor.execute("DELETE FROM users WHERE department_id = %s", (department_id,))
        
        # 4. Finalmente, eliminar el departamento
        cursor.execute("DELETE FROM departments WHERE id = %s", (department_id,))
        
        conn.commit()
        
        return {
            "message": "Departamento eliminado exitosamente",
            "department_name": department[1],
            "deleted_users": user_count,
            "deleted_documents": doc_count,
            "deleted_tables": table_count
        }
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()


def get_department_stats() -> Dict[str, Any]:
    """Obtener estadísticas de departamentos"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Total de departamentos
        cursor.execute("SELECT COUNT(*) FROM departments")
        total_departments = cursor.fetchone()[0]
        
        # Departamentos con usuarios
        cursor.execute("""
            SELECT COUNT(DISTINCT d.id) 
            FROM departments d 
            INNER JOIN users u ON d.id = u.department_id
        """)
        departments_with_users = cursor.fetchone()[0]
        
        # Departamentos con documentos
        cursor.execute("""
            SELECT COUNT(DISTINCT d.id) 
            FROM departments d 
            INNER JOIN documents doc ON d.id = doc.department_id
        """)
        departments_with_documents = cursor.fetchone()[0]
        
        return {
            "totalDepartments": total_departments,
            "departmentsWithUsers": departments_with_users,
            "departmentsWithDocuments": departments_with_documents
        }
    finally:
        cursor.close()
        conn.close()


def get_department_detailed_stats(department_id: int) -> Dict[str, Any]:
    """Obtener estadísticas detalladas de un departamento específico"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Verificar que el departamento existe
        cursor.execute("SELECT id, name FROM departments WHERE id = %s", (department_id,))
        dept_row = cursor.fetchone()
        if not dept_row:
            raise ValueError("Departamento no encontrado")
        
        # Contar usuarios en este departamento
        cursor.execute("SELECT COUNT(*) FROM users WHERE department_id = %s", (department_id,))
        user_count = cursor.fetchone()[0]
        
        # Contar documentos en este departamento
        cursor.execute("SELECT COUNT(*) FROM documents WHERE department_id = %s", (department_id,))
        document_count = cursor.fetchone()[0]
        
        # Contar documentos procesados en este departamento
        cursor.execute("""
            SELECT COUNT(*) FROM documents 
            WHERE department_id = %s AND status = 'processed'
        """, (department_id,))
        processed_documents = cursor.fetchone()[0]
        
        # Contar tablas extraídas de documentos de este departamento
        cursor.execute("""
            SELECT COUNT(*) FROM extracted_tables et
            INNER JOIN documents d ON et.document_id = d.id
            WHERE d.department_id = %s
        """, (department_id,))
        extracted_tables = cursor.fetchone()[0]
        
        return {
            "departmentId": department_id,
            "departmentName": dept_row[1],
            "userCount": user_count,
            "documentCount": document_count,
            "processedDocuments": processed_documents,
            "extractedTables": extracted_tables
        }
    finally:
        cursor.close()
        conn.close()
