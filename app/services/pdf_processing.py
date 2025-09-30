import pdfplumber
from typing import Dict, Any, List
from datetime import datetime


def _normalize_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    return str(value).strip()


def _detect_headers(rows: List[List[str]]) -> Dict[str, Any]:
    """
    Heurística simple: si la primera fila tiene todas las celdas no vacías y al menos 2 columnas,
    se considera header y se devuelve como nombres de columnas.
    """
    if not rows:
        return {"headers": None, "body": rows}
    first = rows[0]
    non_empty = sum(1 for c in first if c and c.strip())
    if non_empty >= max(2, int(len(first) * 0.6)):
        headers = [c.strip() if c else f"col_{i}" for i, c in enumerate(first)]
        body = rows[1:]
        return {"headers": headers, "body": body}
    return {"headers": None, "body": rows}


def extract_pdf_content(file_path: str) -> Dict[str, Any]:
    result: Dict[str, Any] = {
        "summary": "processed",
        "generated_at": datetime.utcnow().isoformat(),
        "pages": [],
        "tables": []  # colección plana (legacy)
    }
    with pdfplumber.open(file_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            page_entry: Dict[str, Any] = {"page": page_index + 1, "text_blocks": [], "tables": []}
            text = page.extract_text() or ""
            if text.strip():
                page_entry["text_blocks"].append(text)
            try:
                raw_tables = page.extract_tables() or []
            except Exception:
                raw_tables = []
            for tbl in raw_tables:
                normalized = [[_normalize_cell(cell) for cell in row] for row in tbl]
                header_info = _detect_headers(normalized)
                entry = {
                    "page": page_index + 1,
                    "headers": header_info["headers"],
                    "rows": header_info["body"]
                }
                page_entry["tables"].append(entry)
                result["tables"].append(entry)
            result["pages"].append(page_entry)
    return result
