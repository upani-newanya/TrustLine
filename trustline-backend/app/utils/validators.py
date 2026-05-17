from fastapi import HTTPException, UploadFile, status


ALLOWED_FILE_TYPES = {
    "image/jpeg": "image",
    "image/png": "image",
    "image/webp": "image",
    "video/mp4": "video",
    "video/quicktime": "video",
    "audio/mpeg": "audio",
    "audio/wav": "audio",
    "application/pdf": "pdf",
}


def validate_upload(upload_file: UploadFile, file_size: int, max_size_bytes: int) -> str:
    if upload_file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed: images, videos, audio, and PDFs.",
        )

    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File is too large. Max allowed size is {max_size_bytes // (1024 * 1024)}MB.",
        )

    return ALLOWED_FILE_TYPES[upload_file.content_type]
