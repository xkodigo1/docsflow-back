import os
from datetime import datetime


def build_upload_path(department_id: int, original_filename: str) -> str:
    base_dir = os.path.join("uploads", f"dept_{department_id}")
    os.makedirs(base_dir, exist_ok=True)
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    safe_name = original_filename.replace(" ", "_")
    return os.path.join(base_dir, f"{timestamp}_{safe_name}")


def write_bytes(filepath: str, data: bytes) -> None:
    with open(filepath, "wb") as f:
        f.write(data)
