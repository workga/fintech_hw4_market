from typing import Any, Optional

from sqlalchemy.exc import SQLAlchemyError


class MarketError(Exception):
    def __init__(
        self,
        message: str = 'Undefined MarketError',
        status_code: int = 400,
        payload: Optional[dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.payload = payload
        self.status_code = status_code

        super().__init__(self.message)

    def as_dict(self) -> dict[str, Any]:
        error_dict = dict(self.payload) if self.payload else {}
        error_dict['message'] = self.message

        return error_dict


class DatabaseError(SQLAlchemyError):
    pass
