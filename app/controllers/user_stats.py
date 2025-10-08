from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from middlewares.auth import get_current_user
from utils.db import get_db_connection

router = APIRouter(prefix="/user-stats", tags=["user-stats"])

@router.get("/dashboard", summary="Obtener estadísticas básicas del usuario", description="Devuelve estadísticas mínimas y optimizadas para el dashboard del usuario.")
def get_user_dashboard_stats(current_user=Depends(get_current_user)) -> Dict[str, Any]:
    try:
        user_id = current_user["id"]
        
        # Una sola consulta optimizada con LIMIT para evitar cargas pesadas
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Consultas simples y robustas
            # Total de documentos
            cursor.execute("SELECT COUNT(*) FROM documents WHERE uploaded_by = %s", (user_id,))
            total_documents = cursor.fetchone()[0] or 0
            
            # Documentos procesados
            cursor.execute("SELECT COUNT(*) FROM documents WHERE uploaded_by = %s AND status = 'processed'", (user_id,))
            processed_documents = cursor.fetchone()[0] or 0
            
            # Documentos pendientes
            cursor.execute("SELECT COUNT(*) FROM documents WHERE uploaded_by = %s AND status = 'pending'", (user_id,))
            pending_documents = cursor.fetchone()[0] or 0
            
            # Documentos fallidos
            cursor.execute("SELECT COUNT(*) FROM documents WHERE uploaded_by = %s AND status = 'failed'", (user_id,))
            failed_documents = cursor.fetchone()[0] or 0
            
            # Total de tablas
            cursor.execute("""
                SELECT COUNT(*) FROM extracted_tables et 
                INNER JOIN documents d ON et.document_id = d.id 
                WHERE d.uploaded_by = %s
            """, (user_id,))
            total_tables = cursor.fetchone()[0] or 0
            
            # Actividad reciente (solo si hay documentos)
            recent_activity = []
            if total_documents > 0:
                cursor.execute("""
                    SELECT filename, status, created_at
                    FROM documents 
                    WHERE uploaded_by = %s 
                    ORDER BY created_at DESC 
                    LIMIT 3
                """, (user_id,))
                
                for row in cursor.fetchall():
                    recent_activity.append({
                        "filename": row[0],
                        "status": row[1],
                        "created_at": row[2].isoformat() if row[2] else None
                    })
            
            # Calcular porcentaje de procesamiento
            processing_rate = (processed_documents / total_documents * 100) if total_documents > 0 else 0
            
            return {
                "user_id": user_id,
                "user_email": current_user["email"],
                "user_role": current_user["role"],
                "summary": {
                    "total_documents": total_documents,
                    "processed_documents": processed_documents,
                    "pending_documents": pending_documents,
                    "failed_documents": failed_documents,
                    "total_tables": total_tables,
                    "processing_rate": round(processing_rate, 1)
                },
                "recent_activity": recent_activity
            }
            
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener estadísticas: {str(e)}"
        )
