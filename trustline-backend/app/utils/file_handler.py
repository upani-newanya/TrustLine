from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


def save_upload_file(upload_file: UploadFile, upload_dir: str) -> tuple[str, str, int, str]:
    upload_path = Path(upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)

    suffix = Path(upload_file.filename or "").suffix
    generated_name = f"{uuid4().hex}{suffix}"
    full_path = upload_path / generated_name

    file_bytes = upload_file.file.read()
    size = len(file_bytes)

    with full_path.open("wb") as f:
        f.write(file_bytes)

    return generated_name, str(full_path), size, (upload_file.filename or generated_name)
