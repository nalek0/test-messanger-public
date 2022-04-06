from werkzeug.exceptions import BadRequestKeyError


class APIException(Exception):
    status_code: int

    @property
    def dict(self) -> dict:
        return {
            "status": self.status_code,
            "description": self.description
        }

    def __init__(self, description: str) -> None:
        super().__init__()
        self.description = description


class APIBadRequest(APIException):
    status_code = 400

    @classmethod
    def make_from(cls, exception: BadRequestKeyError) -> APIException:
        return cls(exception.description)


class APIUnauthorized(APIException):
    status_code = 401

    def __init__(self) -> None:
        super().__init__("This method requires authentication")


class APIForbidden(APIException):
    status_code = 403


class APINotFound(APIException):
    status_code = 404
