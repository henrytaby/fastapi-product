class CustomException(Exception):
    def __init__(self, detail: str):
        self.detail = detail


class NotFoundException(CustomException):
    """Raised when a resource is not found."""

    pass


class BadRequestException(CustomException):
    """Raised when a request is invalid."""

    pass


class InternalServerErrorException(CustomException):
    """Raised when an unexpected error occurs."""

    pass
