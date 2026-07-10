from http import HTTPStatus


class AppError(Exception):
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR
    message: str = "An unexpected application error occurred."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.message
        super().__init__(self.message)


class ResourceNotFoundError(AppError):
    status_code = HTTPStatus.NOT_FOUND
    message = "Requested resource was not found."


class BadRequestError(AppError):
    status_code = HTTPStatus.BAD_REQUEST
    message = "Bad request."
