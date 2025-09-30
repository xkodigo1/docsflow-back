# Procesamiento de PDFs en DocsFlow

Este documento describe cómo se realiza la extracción de texto y tablas de los PDFs y su integración con los endpoints.

## Flujo general

1. El usuario sube un PDF vía `POST /documents/upload`.
2. Un admin u operador procesa el documento vía `POST /documents/{id}/process`.
3. El backend extrae texto y tablas, guarda el JSON en `extracted_tables` y marca el documento como `processed`.

## Implementación

- Servicio: `app/services/pdf_processing.py`
  - Función `extract_pdf_content(file_path: str) -> dict`.
  - Usa `pdfplumber` para leer cada página, extraer texto (`extract_text`) y tablas (`extract_tables`).
  - Estructura devuelta:
    ```json
    {
      "summary": "processed",
      "text_blocks": ["texto pagina 1", "texto pagina 2", ...],
      "tables": [
        { "rows": [["col1","col2"], ["v1","v2"]] },
        ...
      ]
    }
    ```

- Endpoint: `app/controllers/documents.py`
  - `POST /documents/{id}/process`:
    - Valida permisos por rol/departamento.
    - Llama a `extract_pdf_content(path)`.
    - Inserta el JSON en `extracted_tables.content`.
    - Actualiza `documents.status = 'processed'` y `processed_at = NOW()`.

## Notas

- Tamaño máximo de archivo: 15MB (configurable en el controlador de upload).
- Manejo de errores: si `extract_tables` falla en una página, se captura y continúa.
- Futuras mejoras: extracción semántica, normalización de tablas (headers), exportación a CSV/Excel.
