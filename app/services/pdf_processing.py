import pdfplumber
from typing import Dict, Any, List

def extract_pdf_content(file_path: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "summary": "processed",
        "text_blocks": [],
        "tables": []
    }
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                result["text_blocks"].append(text)
            try:
                tables = page.extract_tables()
            except Exception:
                tables = []
            for tbl in tables or []:
                # Normalizar filas eliminando None
                normalized = [[cell if cell is not None else "" for cell in row] for row in tbl]
                result["tables"].append({
                    "rows": normalized
                })
    return result
