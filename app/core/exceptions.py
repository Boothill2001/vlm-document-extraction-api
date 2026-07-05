from fastapi import HTTPException


class ExtractionError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=422, detail=detail)


class ProviderError(HTTPException):
    def __init__(self, provider: str, detail: str):
        super().__init__(
            status_code=502,
            detail=f"Provider '{provider}' error: {detail}",
        )


class UnsupportedFileError(HTTPException):
    def __init__(self, filename: str):
        super().__init__(
            status_code=400,
            detail=f"Unsupported file type: {filename}. Supported: .pdf, .png, .jpg, .jpeg, .txt",
        )


class FileTooLargeError(HTTPException):
    def __init__(self, size_mb: float, max_mb: int):
        super().__init__(
            status_code=413,
            detail=f"File size {size_mb:.1f}MB exceeds limit of {max_mb}MB",
        )
