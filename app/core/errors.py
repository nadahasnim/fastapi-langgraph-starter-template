class AppError(Exception):
    """Base application exception with structured error details."""

    def __init__(self, message: str, status_code: int = 500, code: str = "internal_error"):
        self.message = message
        self.status_code = status_code
        self.code = code
        super().__init__(message)
