from __future__ import annotations


class AppError(Exception):
    status_code = 500
    code = "internal"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ValidationAppError(AppError):
    status_code = 400
    code = "validation"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


class DomainNotConfiguredError(AppError):
    status_code = 501
    code = "not_configured"


class ScriptRunnerError(AppError):
    status_code = 502
    code = "script_failed"
